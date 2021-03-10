"""Map class module."""
from __future__ import annotations

import collections
from typing import Deque, NamedTuple, Set, Tuple

import numpy as np

import engine.actor
import engine.sched
import engine.tiles
from engine.tiles import TILE_DT


class Camera(NamedTuple):
    """An object for tracking the camera position and for screen/world conversions.

    `x` and `y` are the camera center position.
    """

    x: int
    y: int

    def get_left_top_pos(self, screen_shape: Tuple[int, int]) -> Tuple[int, int]:
        """Return the (left, top) position of the camera for a screen of this size."""
        return self.x - screen_shape[0] // 2, self.y - screen_shape[1] // 2

    def get_views(
        self, world_shape: Tuple[int, int], screen_shape: Tuple[int, int]
    ) -> Tuple[Tuple[slice, slice], Tuple[slice, slice]]:
        """Return (screen_view, world_view) as 2D slices for use with NumPy.

        These views are used to slice their respective arrays.
        """
        camera_left, camera_top = self.get_left_top_pos(screen_shape)

        screen_left = max(0, -camera_left)
        screen_top = max(0, -camera_top)

        world_left = max(0, camera_left)
        world_top = max(0, camera_top)

        screen_width = min(screen_shape[0] - screen_left, world_shape[0] - world_left)
        screen_height = min(screen_shape[1] - screen_top, world_shape[1] - world_top)

        screen_view: Tuple[slice, slice] = np.s_[
            screen_left : screen_left + screen_width,
            screen_top : screen_top + screen_height,
        ]
        world_view: Tuple[slice, slice] = np.s_[
            world_left : world_left + screen_width,
            world_top : world_top + screen_height,
        ]

        return screen_view, world_view


class Map:
    """Maps hold a descrete set of data which can be switched between more easily."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles = np.empty((width, height), TILE_DT, order="F")
        self.tiles[:] = engine.tiles.DEFAULT
        self.memory: np.ndarray = np.full((width, height), engine.rendering.SHROUD, order="F")
        self.actors: Set[engine.actor.Actor] = set()
        self.schedule: Deque[engine.sched.Schedulable] = collections.deque()
        self.camera: Camera = Camera(0, 0)

    def add_actor(self, actor: engine.actor.Actor) -> None:
        assert actor not in self.actors
        self.actors.add(actor)
        self.schedule.append(actor)

    def remove_actor(self, actor: engine.actor.Actor) -> None:
        self.actors.remove(actor)
        self.schedule.remove(actor)

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns True if `x`,`y` is in bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x: int, y: int) -> bool:
        """Returns True if this space can accept a large object such as an Actor."""
        if not self.in_bounds(x, y):
            return True  # Out-of-bounds.
        if not self.tiles["move_cost"][x, y]:
            return True  # Blocked by tile.
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return True  # Space taken by actor.
        return False
