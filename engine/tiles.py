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
        ("dangerous", bool),
    ]
)


class Tile(NamedTuple):
    """A NamedTuple type broadcastable to any TILE_DT array."""

    move_cost: int
    transparent: bool
    graphic: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
    effect: Optional[engine.effects.Effect] = None
    dangerous: bool = False

    def as_np(self) -> np.ndarray:
        """Return this tile as an array scaler."""
        return np.asarray(self, dtype=TILE_DT)


# Tiles color scheme:
# https://paletton.com/#uid=7000H0kmOpCsM5UrxfxiMyhdzSk
DEFAULT = WALL = Tile(
    move_cost=0,
    transparent=False,
    graphic=(ord(" "), (255, 255, 255), (47, 29, 5)),
)
FLOOR = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord("."), (255, 190, 105), (124, 77, 17)),
)
RUBBLE = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord(","), (0, 0, 0), (124, 77, 17)),
)

WATER = Tile(
    move_cost=0,
    transparent=True,
    graphic=(ord("~"), (139, 192, 230), (15, 52, 79)),
)

ICE_FLOOR = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord("+"), (0xFF, 0xFF, 0xFF), (77, 131, 170)),
)
ICE_WALL = Tile(
    move_cost=0,
    transparent=True,
    graphic=(ord("="), (0xFF, 0xFF, 0xFF), (77, 131, 170)),
)

ACID = Tile(
    move_cost=1,
    transparent=True,
    graphic=(ord("°"), (0xFF, 0xFF, 0xFF), (86, 208, 86)),
    effect=Effect(power=1),
    dangerous=True,
)
