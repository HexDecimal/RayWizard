from __future__ import annotations

from typing import NamedTuple, Tuple

import numpy as np

tile_graphic = np.dtype([("ch", np.int32), ("fg", "3B"), ("bg", "3B")])


class Tile(NamedTuple):
    """A NamedTuple type broadcastable to any TILE_DT array."""

    move_cost: int
    transparent: bool
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]


DEFAULT = Tile(
    move_cost=0,
    transparent=False,
    light=(ord(" "), (255, 255, 255), (130, 110, 50)),
    dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
)

WALL = Tile(
    move_cost=0,
    transparent=False,
    light=(ord(" "), (130, 110, 50), (200, 180, 50)),
    dark=(ord(" "), (25, 25, 75), (50, 50, 100)),
)
FLOOR = Tile(
    move_cost=1,
    transparent=True,
    light=(ord("."), (130, 110, 50), (200, 180, 50)),
    dark=(ord("."), (25, 25, 75), (50, 50, 150)),
)

WATER = Tile(
    move_cost=0,
    transparent=True,
    light=(ord("~"), (130, 110, 50), (200, 180, 50)),
    dark=(ord("~"), (25, 25, 75), (50, 50, 150)),
)
