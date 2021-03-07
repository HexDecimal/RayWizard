"""A collection of combat effects."""
from __future__ import annotations

import engine.tiles
import g


class Effect:
    def apply(self, x: int, y: int) -> None:
        pass


class Cold(Effect):
    def apply(self, x: int, y: int) -> None:
        if g.world.map.tiles[x, y] == engine.tiles.WATER.as_np():
            g.world.map.tiles[x, y] = engine.tiles.ICE_FLOOR


class Heat(Effect):
    def apply(self, x: int, y: int) -> None:
        if g.world.map.tiles[x, y] == engine.tiles.ICE_FLOOR.as_np():
            g.world.map.tiles[x, y] = engine.tiles.WATER
