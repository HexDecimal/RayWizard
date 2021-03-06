"""Map class module."""
from __future__ import annotations

import collections
from typing import Deque, NamedTuple, Set, Tuple

import numpy as np

import engine.actor
import engine.sched

#TILE_DT = np.dtype([("ch", np.int32)])

tile_graphic = np.dtype([("ch", np.int32), ("fg", "3B"), ("bg", "3B")])
TILE_DT = np.dtype(
    [
        ("move_cost", np.uint8),
        ("transparent", bool),
        ("light", tile_graphic),
        ("dark", tile_graphic),
    ]
)


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

class Tile(NamedTuple):
    """A NamedTuple type broadcastable to any tile_dt array."""

    move_cost: int
    transparent: bool
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]

class Map:
    """Maps hold a descrete set of data which can be switched between more easily."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), ord("."), TILE_DT, order="F")
        self.actors: Set[engine.actor.Actor] = set()
        self.schedule: Deque[engine.sched.Schedulable] = collections.deque()
        self.camera = Camera(0, 0)

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
