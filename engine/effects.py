"""A collection of combat effects."""
from __future__ import annotations

import engine.tiles
import g


class Effect:
    name = "stuff"

    def __init__(self, power: int = 5):
        self.power = power

    def apply(self, x: int, y: int) -> None:
        for actor in [actor for actor in g.world.map.actors if x == actor.x and y == actor.y]:
            actor.apply_effect(self)


class Cold(Effect):
    name = "ice"

    def apply(self, x: int, y: int) -> None:
        super().apply(x, y)
        if g.world.map.tiles[x, y] == engine.tiles.WATER.as_np():
            g.world.map.tiles[x, y] = engine.tiles.ICE_FLOOR
        if g.world.map.tiles[x, y] == engine.tiles.ACID.as_np():
            g.world.map.tiles[x, y] = engine.tiles.ICE_FLOOR


class Heat(Effect):
    name = "fire"

    def apply(self, x: int, y: int) -> None:
        super().apply(x, y)
        if g.world.map.tiles[x, y] == engine.tiles.ICE_FLOOR.as_np():
            g.world.map.tiles[x, y] = engine.tiles.WATER
        if g.world.map.tiles[x, y] == engine.tiles.ICE_WALL.as_np():
            g.world.map.tiles[x, y] = engine.tiles.WATER


class PlaceAcid(Effect):
    name = "acid"

    def apply(self, x: int, y: int) -> None:
        super().apply(x, y)
        g.world.map.tiles[x, y] = engine.tiles.ACID


class Dig(Effect):
    name = "digging"

    def apply(self, x: int, y: int) -> None:
        super().apply(x, y)
        if g.world.map.tiles[x, y] == engine.tiles.WALL.as_np():
            g.world.map.tiles[x, y] = engine.tiles.RUBBLE
        if g.world.map.tiles[x, y] == engine.tiles.ICE_WALL.as_np():
            g.world.map.tiles[x, y] = engine.tiles.ICE_FLOOR
