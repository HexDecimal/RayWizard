"""Map class module."""
from __future__ import annotations

from typing import Set

import numpy as np

import engine.actor

TILE_DT = np.dtype([("ch", np.int32)])


class Map:
    """Maps hold a descrete set of data which can be switched between more easily."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), ord("."), TILE_DT, order="F")
        self.actors: Set[engine.actor.Actor] = set()

    def is_not_blocked(self, x: int, y: int) -> bool:
        """Returns True if this space can accept a large object such as an Actor."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False  # Out-of-bounds.
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return False  # Space taken by actor.
        return True
