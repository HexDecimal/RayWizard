from __future__ import annotations

from typing import NamedTuple, Optional, Tuple

import numpy as np

import engine.effects
from engine.effects import Effect

tile_graphic = np.dtype([("ch", np.int32), ("fg", "3B"), ("bg", "3B")])

TILE_DT = np.dtype(
    [
        ("move_cost", np.uint8),
        ("transparent", bool),
        ("graphic", tile_graphic),
        ("effect", object),
    ]
)


class Tile(NamedTuple):
    """A NamedTuple type broadcastable to any TILE_DT array."""

    move_cost: int
    transparent: bool
    graphic: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
    effect: Optional[engine.effects.Effect] = None

    def as_np(self) -> np.ndarray:
        """Return this tile as an array scaler."""
        return np.asarray(self, dtype=TILE_DT)


DEFAULT = Tile(
    move_cost=0,
    transparent=False,
    graphic=(ord(" "), (255, 255, 255), (0, 0, 100)),
)

WALL = Tile(
    move_cost=0,
    transparent=False,
    graphic=(ord(" "), (25, 25, 75), (50, 50, 100)),
)
FLOOR = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord("."), (25, 25, 75), (50, 50, 150)),
)
RUBBLE = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord(","), (25, 25, 75), (50, 50, 150)),
)

WATER = Tile(
    move_cost=0,
    transparent=True,
    graphic=(ord("~"), (0x40, 0x40, 0x40), (0x10, 0x10, 0xFF)),
)

ICE_FLOOR = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord("+"), (0xFF, 0xFF, 0xFF), (0x22, 0xFF, 0xFF)),
)
ICE_WALL = Tile(
    move_cost=0,
    transparent=True,
    graphic=(ord("="), (0xFF, 0xFF, 0xFF), (0x22, 0xFF, 0xFF)),
)

ACID = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord("~"), (0x40, 0x40, 0x40), (0x10, 0xB0, 0x10)),
    effect=Effect(power=1),
)
