"""Dungeon level generator."""
from __future__ import annotations

import random
from typing import Iterator, List, Tuple

import numpy as np
import scipy.signal
import tcod

import engine.map
import engine.world

WALL = engine.map.Tile(
    move_cost=0,
    transparent=False,
    light=(ord(" "), (130, 110, 50), (200, 180, 50)),
    dark=(ord(" "), (25, 25, 75), (50, 50, 100)),
)
FLOOR = engine.map.Tile(
    move_cost=1,
    transparent=True,
    light=(ord("."), (130, 110, 50), (200, 180, 50)),
    dark=(ord("."), (25, 25, 75), (50, 50, 150)),
)

WATER = engine.map.Tile(
    move_cost=0,
    transparent=True,
    light=(ord("~"), (130, 110, 50), (200, 180, 50)),
    dark=(ord("~"), (25, 25, 75), (50, 50, 150)),
)


class Room:
    """Holds data and methods used to generate rooms."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def outer(self) -> Tuple[slice, slice]:
        """Return the NumPy index for the whole room."""
        index: Tuple[slice, slice] = np.s_[self.x1 : self.x2, self.y1 : self.y2]
        return index

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the NumPy index for the inner room area."""
        index: Tuple[slice, slice] = np.s_[self.x1 + 1 : self.x2 - 1, self.y1 + 1 : self.y2 - 1]
        return index

    @property
    def center(self) -> Tuple[int, int]:
        """Return the index for the rooms center coordinate."""
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def intersects(self, other: Room) -> bool:
        """Return True if this room intersects with another."""
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1

    def distance_to(self, other: Room) -> float:
        """Return an approximate distance from this room to another."""
        x, y = self.center
        other_x, other_y = other.center
        return abs(other_x - x) + abs(other_y - y)

    def get_free_spaces(self, gamemap: engine.map.Map, number: int) -> Iterator[Tuple[int, int]]:
        """Iterate over the x,y coordinates of up to `number` spaces."""
        for _ in range(number):
            x = random.randint(self.x1 + 1, self.x2 - 2)
            y = random.randint(self.y1 + 1, self.y2 - 2)
            if gamemap.is_blocked(x, y):
                continue
            yield x, y


# creates smooth caves/water given noise or current map position.
def convolve(tiles: np.ndarray, wall_rule: int = 5) -> np.ndarray:
    """Return the next step of the cave generation algorithm.
    `tiles` is the input array. (0: wall, 1: floor)
    If the 3x3 area around a tile (including itself) has `wall_rule` number of
    walls then the tile will become a wall.
    """

    # Use convolve2d, the 2nd input is a 5x5 array, with a core 3x3 of 2s surrounded by 1s.
    neighbors = scipy.signal.convolve2d(
        ~tiles, [[1, 1, 1, 1, 1], [1, 2, 2, 2, 1], [1, 2, 2, 2, 1], [1, 2, 2, 2, 1], [1, 1, 1, 1, 1]], "same"
    )
    return neighbors < wall_rule  # type: ignore  # Apply the wall rule.


# creates a map of unifrom random noise to feed into cave and water generators.
# We could use a frequency base noise generator if we want to have features of a particular general size.
# But, as we only really have 2 states rather than a range like for an elevation generator.
# TRis should suffice.
# WallPrecent is an integer which represents what portion out 100 should be spawned with walls.
# Walls are 0s in output.
def createNoiseMap(theWidth: int, theHeight: int, wallPercent: int) -> np.ndarray:
    theTiles = np.full((theWidth, theHeight), -1, order="F")
    for theX in range(theWidth):
        for theY in range(theHeight):
            if random.randint(0, 100) < wallPercent:
                theTiles[theX, theY] = 0
            else:
                theTiles[theX, theY] = 1
    return theTiles


def generate(model: engine.world.World, width: int = 80, height: int = 45) -> engine.map.Map:
    """Return a randomly generated GameMap."""
    room_max_size = 20
    room_min_size = 4
    max_rooms = 100
    # close_room = False

    gm = engine.map.Map(width, height)
    gm.tiles[...] = WALL
    rooms: List[Room] = []

    for _ in range(max_rooms):
        # random width and height
        w = random.randint(room_min_size, room_max_size)
        h = random.randint(room_min_size, room_max_size)
        # random position without going out of the boundaries of the map
        x = random.randint(0, width - w)
        y = random.randint(0, height - h)
        new_room = Room(x, y, w, h)
        if any(new_room.intersects(other) for other in rooms):
            continue  # This room intersects with a previous room.

        # Mark room inner area as open.
        gm.tiles[new_room.inner] = FLOOR
        if rooms:
            # Open a tunnel between rooms.
            if random.randint(0, 99) < 80:
                # 80% of tunnels are to the nearest room.
                other_room = min(rooms, key=new_room.distance_to)
                # close_rooom = True
            else:
                # 20% of tunnels are to the previous generated room.
                other_room = rooms[-1]
                # close_rooom = False
            t_start = new_room.center
            t_end = other_room.center
            if random.randint(0, 1):
                t_middle = t_start[0], t_end[1]
            else:
                t_middle = t_end[0], t_start[1]
            gm.tiles[tcod.line_where(*t_start, *t_middle)] = FLOOR
            gm.tiles[tcod.line_where(*t_middle, *t_end)] = FLOOR
            # if close_room = False:
            # gm.tiles[tcod.line_where(*t_start, *t_middle-1)] = FLOOR
            # gm.tiles[tcod.line_where(*t_middle-1, *t_end-1)] = FLOOR
        rooms.append(new_room)

    # Start of Water generation:
    # step 1 make random map noise:
    randomMap = createNoiseMap(width, height, 75)

    # step 2: feed to cellular automata sevewral times (number of times based on tweaking.
    automataMap1 = convolve(randomMap, 10)  # second value is the number of nearby tiles needed to be water.

    # step 3: Use map to replace wall and floor tiles with water.
    for theX in range(width):
        for theY in range(height):
            if automataMap1[theX, theY] == 1:
                gm.tiles[theX, theY] = WATER

    # Add player to the first room.
    model.player = engine.actor.Actor(*rooms[0].center)
    gm.add_actor(model.player)

    return gm
