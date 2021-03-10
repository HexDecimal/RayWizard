"""A collection of combat effects."""
from __future__ import annotations

import engine.tiles
import g


class Effect:
    def __init__(self, power: int = 5):
        self.power = power

    def apply(self, x: int, y: int) -> None:
        for actor in [actor for actor in g.world.map.actors if x == actor.x and y == actor.y]:
            actor.apply_effect(self)


class Cold(Effect):
    def apply(self, x: int, y: int) -> None:
        super().apply(x, y)
        if g.world.map.tiles[x, y] == engine.tiles.WATER.as_np():
            g.world.map.tiles[x, y] = engine.tiles.ICE_FLOOR


class Heat(Effect):
    def apply(self, x: int, y: int) -> None:
        super().apply(x, y)
        if g.world.map.tiles[x, y] == engine.tiles.ICE_FLOOR.as_np():
            g.world.map.tiles[x, y] = engine.tiles.WATER
