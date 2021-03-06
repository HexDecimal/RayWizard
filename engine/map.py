"""Map class module."""
from __future__ import annotations

import collections
from typing import Deque, Set

import numpy as np

import engine.actor
import engine.sched

TILE_DT = np.dtype([("ch", np.int32)])


class Map:
    """Maps hold a descrete set of data which can be switched between more easily."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), ord("."), TILE_DT, order="F")
        self.actors: Set[engine.actor.Actor] = set()
        self.schedule: Deque[engine.sched.Schedulable] = collections.deque()

    def add_actor(self, actor: engine.actor.Actor) -> None:
        assert actor not in self.actors
        self.actors.add(actor)
        self.schedule.append(actor)

    def remove_actor(self, actor: engine.actor.Actor) -> None:
        self.actors.remove(actor)
        self.schedule.remove(actor)

    def is_not_blocked(self, x: int, y: int) -> bool:
        """Returns True if this space can accept a large object such as an Actor."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False  # Out-of-bounds.
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return False  # Space taken by actor.
        return True
