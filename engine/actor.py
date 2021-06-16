"""Actor class module"""
from __future__ import annotations

from typing import Dict, Optional, Tuple
import logging

import numpy as np
import tcod

from engine.sched import Schedulable
import engine.actions
import engine.map
import engine.states
import g

logger = logging.getLogger(__name__)


class Actor(Schedulable):
    """Objects which are able to move on their own."""

    name = "<actor>"
    ch = "X"
    fg = (0xFF, 0xFF, 0xFF)
    hp: int = 10
    faction = "hostile"
    share_vision: bool = False  # If True this object shares vision with its own faction.
    can_walk = True
    can_fly = False
    can_swim = False
    view_radius: int = 10

    def __init__(
        self,
        x: int,
        y: int,
        *,
        faction: Optional[str] = None,
    ):
        self.x = x
        self.y = y
        self.skip_turns = 0  # Add to this to skip this actors turns.
        self.ai: Optional[engine.actions.Action] = None  # Cached AI action.
        if faction is not None:
            self.faction = faction
        self.status: Dict[str, int] = {}  # Status effects: Dict[status_name: time_left]

    def default_ai(self) -> engine.actions.Action:
        """Return the action that this actor should perform."""
        return engine.actions.IdleAction(self)

    def on_turn(self) -> None:
        """Perform this actors action until False is returned, then refresh the action."""
        if not self.ai:
            self.ai = self.default_ai()
        if not self.ai.perform():
            self.ai = None

    def on_end_turn(self) -> None:
        """Called after a turn has passed."""
        for name in list(self.status):
            self.status[name] -= 1
            if self.status[name] == 0:
                del self.status[name]
                g.world.report(f"{name.title()} has worn off.")
        # Apply tile to the actor.
        tile_effect: Optional[engine.effects.Effect] = g.world.map.tiles["effect"][self.xy]
        if tile_effect:
            tile_effect.apply(*self.xy)

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        """Take damage or trigger side-effects."""
        damage = effect.power  # Placeholder.
        g.world.report(f"{self.name.title()} takes {damage} damage.", visual_xy=self.xy)
        self.hp -= damage
        if self.hp <= 0:
            g.world.report(f"{self.name.title()} dies.", visual_xy=self.xy)
            g.world.map.remove_actor(self)

    @property
    def xy(self) -> Tuple[int, int]:
        """This actors current position."""
        return self.x, self.y

    def get_fov(self, plus_shared: bool = True) -> np.ndarray:
        """Return a bool array of tiles this actor can see.

        If `plus_shared` is True then shared vision is also added.  This parameter is used to prevent infinite
        recursion.
        """
        visible = tcod.map.compute_fov(
            transparency=g.world.map.tiles["transparent"],
            pov=self.xy,
            algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST,
            radius=self.view_radius,
        )
        if "earth vision" in self.status:
            visible |= tcod.map.compute_fov(
                transparency=~g.world.map.tiles["transparent"],
                pov=self.xy,
                algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST,
                radius=0,
            )
        if plus_shared:
            for actor in g.world.map.actors:
                if actor is self or actor.share_vision is False or actor.faction != self.faction:
                    continue
                visible |= actor.get_fov(plus_shared=False)
        return visible

    def get_move_cost(self) -> np.ndarray:
        """Get the real move cost of an actor."""
        if self.can_walk is True and self.can_swim is False and self.can_fly is False:
            return g.world.map.tiles["move_cost"].copy()  # type: ignore

        # This fallback will have to do for now.
        cost: np.ndarray = np.zeros_like(g.world.map.tiles, dtype=np.uint8)
        if self.can_swim:
            np.putmask(cost, g.world.map.tiles["swim_cost"] != 0, g.world.map.tiles["swim_cost"])
        if self.can_walk:
            np.putmask(cost, g.world.map.tiles["move_cost"] != 0, g.world.map.tiles["move_cost"])
        if self.can_fly:
            np.putmask(cost, g.world.map.tiles["fly_cost"] != 0, g.world.map.tiles["fly_cost"])
        return cost

    def bump(self, other: Actor) -> bool:
        """Called when one actor bumps into another.

        Should return False if nothing that should take a turn has happened.
        """
        return False


class Player(Actor):
    name = "player"
    ch = "@"
    faction = "player"
    hp = 12

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.PlayerControl(self)


class Scout(Actor):
    name = "scout"
    ch = "s"
    faction = "player"
    share_vision = True
    hp = 1
    can_fly = True

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.Explore(self)


class Bomb(Actor):
    """Counts down to zero and then deletes nearby actors."""

    name = "bomb"
    faction = "player"

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.timer = 5
        self.ch = str(self.timer)

    def explode(self) -> None:
        engine.actions.Blast(self, effect=engine.effects.Dig(power=10), range=2).perform()
        if self in g.world.map.actors:
            g.world.map.remove_actor(self)

    def on_turn(self) -> None:
        super().on_turn()
        self.timer -= 1
        if self.timer < 0:
            self.explode()
        else:
            self.ch = str(self.timer)

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        """Explodes immediately if hit with a heat attacks."""
        if isinstance(effect, engine.effects.Heat):
            self.explode()


class Totem(Actor):
    name = "totem"
    faction = "player"

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.ch = "&"

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        g.world.map.remove_actor(self)
        for y in range(self.y - 2, self.y + 3):
            for x in range(self.x - 2, self.x + 3):
                effect.apply(x, y)


class FlyingBomb(Bomb):
    name = "flying bomb"
    faction = "player"

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.SeekEnemy(self)


class HunterEnemy(Actor):
    name = "hunter"
    faction = "hostile"
    attack_effect = engine.effects.PlaceAcid(power=2)  # does two damage

    def bump(self, other: Actor) -> bool:
        if other.faction != self.faction:
            self.attack_effect.apply(*other.xy)
            return True
        return False

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.SeekEnemy(self)


class HeatBoltEnemy(Actor):
    name = "fire caster"
    faction = "hostile"
    ch = "H"

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.RangedIdle(self, effect=engine.effects.Heat(power=2), range=3)


class ColdBoltEnemy(Actor):
    name = "ice caster"
    faction = "hostile"
    ch = "C"

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.RangedIdle(self, effect=engine.effects.Cold(power=1), range=2)


class AcidBoltEnemy(Actor):
    name = "acid caster"
    faction = "hostile"
    ch = "A"

    def default_ai(self) -> engine.actions.Action:
        return engine.actions.RangedIdle(self, effect=engine.effects.PlaceAcid(power=1), range=1)
