"""Actor class module"""
from __future__ import annotations

import logging

import engine.map
import engine.states
import g
from engine.sched import Schedulable

logger = logging.getLogger(__name__)


class Actor(Schedulable):
    """Objects which are able to move on their own."""

    ch = "@"
    fg = (0xFF, 0xFF, 0xFF)

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def on_turn(self) -> None:
        if self is g.world.player:
            logger.info("Player turn")
            g.world.map.camera = engine.map.Camera(self.x, self.y)
            engine.states.InGame().run_modal()
            return
        logger.info(f"Non-Player turn: {self}")

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        """Take damage or trigger side-effects."""


class Bomb(Actor):
    """Counts down to zero and then deletes nearby actors."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.timer = 5
        self.ch = str(self.timer)

    def explode(self) -> None:
        # Should be replaced by an effect.
        for actor in list(g.world.map.actors):
            dist = abs(actor.x - self.x) + abs(actor.y - self.y)
            if dist <= 2:
                g.world.map.remove_actor(actor)

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
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.ch = "&"

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        g.world.map.remove_actor(self)
        for y in range(self.y - 2, self.y + 3):
            for x in range(self.x - 2, self.x + 3):
                effect.apply(x, y)
