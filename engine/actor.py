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
