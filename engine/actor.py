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


class Bomb(Actor):
    """Counts down to zero and then deletes nearby actors."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.timer = 5
        self.ch = str(self.timer)

    def on_turn(self) -> None:
        self.timer -= 1
        if self.timer < 0:
            for actor in list(g.world.map.actors):
                dist = abs(actor.x - self.x) + abs(actor.y - self.y)
                if dist <= 2:
                    g.world.map.remove_actor(actor)
        else:
            self.ch = str(self.timer)
