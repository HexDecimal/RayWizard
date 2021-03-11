"""Actor class module"""
from __future__ import annotations

import logging
from typing import Callable, Optional, Tuple

import numpy as np
import tcod

import engine.actions
import engine.map
import engine.states
import g
from engine.sched import Schedulable

logger = logging.getLogger(__name__)


class Actor(Schedulable):
    """Objects which are able to move on their own."""

    ch = "X"
    fg = (0xFF, 0xFF, 0xFF)
    faction = "hostile"

    def __init__(
        self,
        x: int,
        y: int,
        *,
        ai: Optional[Callable[[Actor], engine.actions.Action]] = None,
        faction: Optional[str] = None,
    ):
        self.x = x
        self.y = y
        self.hp = 10
        self.skip_turns = 0  # Add to this to skip this actors turns.
        if faction is not None:
            self.faction = faction

    def on_turn(self) -> None:
        raise NotImplementedError("on_turn must be overridden.")

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        """Take damage or trigger side-effects."""
        damage = effect.power  # Placeholder.
        g.world.report(f"{self} takes {damage} damage.")
        self.hp -= damage
        if self.hp <= 0:
            g.world.report(f"{self} dies.")
            g.world.map.remove_actor(self)

    @property
    def xy(self) -> Tuple[int, int]:
        """This actors current position."""
        return self.x, self.y

    def get_fov(self) -> np.ndarray:
        """Return a bool array of tiles this actor can see."""
        return tcod.map.compute_fov(
            transparency=g.world.map.tiles["transparent"], pov=self.xy, algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST
        )

    def bump(self, other: Actor) -> bool:
        """Called when one actor bumps into another.

        Should return False if nothing that should take a turn has happened.
        """
        return False


class Player(Actor):
    ch = "@"
    faction = "player"

    def on_turn(self) -> None:
        engine.actions.PlayerControl(self).perform()


class Bomb(Actor):
    """Counts down to zero and then deletes nearby actors."""

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
    faction = "player"

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.ch = "&"

    def on_turn(self) -> None:
        pass

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        g.world.map.remove_actor(self)
        for y in range(self.y - 2, self.y + 3):
            for x in range(self.x - 2, self.x + 3):
                effect.apply(x, y)


class FlyingBomb(Bomb):
    faction = "player"

    def on_turn(self) -> None:
        super().on_turn()
        engine.actions.SeekEnemy(self).perform()


class HunterEnemy(Actor):
    faction = "hostile"
    attack_effect = engine.effects.PlaceAcid(power=2)  # does two damage

    def bump(self, other: Actor) -> bool:
        if other.faction != self.faction:
            self.attack_effect.apply(*other.xy)
            return True
        return False

    def on_turn(self) -> None:
        engine.actions.SeekEnemy(self).perform()


class HeatBoltEnemy(Actor):
    faction = "hostile"

    def on_turn(self) -> None:
        engine.actions.RangedIdle(self, effect=engine.effects.Heat(power=2), range=2).perform()


class ColdBoltEnemy(Actor):
    faction = "hostile"

    def on_turn(self) -> None:
        engine.actions.RangedIdle(self, effect=engine.effects.Cold(power=1), range=2).perform()
