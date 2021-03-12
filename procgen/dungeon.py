"""Dungeon level generator."""
from __future__ import annotations

import random
from typing import Iterator, List, Tuple

import numpy as np
import scipy.signal  # type: ignore
import tcod

import engine.actions
import engine.features
import engine.map
import engine.rendering
import engine.tiles
import engine.world


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
            if gamemap.is_blocked(x, y, None):
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
        tiles == 0, [[1, 1, 1, 1, 1], [1, 2, 2, 2, 1], [1, 2, 2, 2, 1], [1, 2, 2, 2, 1], [1, 1, 1, 1, 1]], "same"
    )
    return neighbors < wall_rule  # type: ignore  # Apply the wall rule.


def create_noise_map(width: int, height: int, wall_percent: int) -> np.ndarray:
    """Creates a map of unifrom random noise to feed into cave and water generators.

    We could use a frequency base noise generator if we want to have features of a particular general size.
    But, as we only really have 2 states rather than a range like for an elevation generator.
    TRis should suffice.
    `wall_percent` is an integer which represents what portion out 100 should be spawned with walls.
    Walls are False in output.
    """
    return np.random.random((height, width)).transpose() < wall_percent / 100  # type: ignore


def generate(
    model: engine.world.World,
    level: int,
    width: int = 80,
    height: int = 45,
    room_max_size: int = 20,
) -> engine.map.Map:
    """Return a randomly generated GameMap."""
    wallType = engine.tiles.WALL
    waterType = engine.tiles.WATER

    if level == 2:
        wallType = engine.tiles.ICE_WALL
    if level == 3:
        waterType = engine.tiles.ACID

    room_min_size = 4
    max_rooms = 100

    gm = engine.map.Map(width, height, level=level)
    gm.tiles[...] = wallType
    engine.rendering.debug_map(gm)
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
        gm.tiles[new_room.inner] = engine.tiles.FLOOR
        engine.rendering.debug_map(gm)
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
            tunnel_indices = np.r_[
                tcod.los.bresenham(t_start, t_middle), tcod.los.bresenham(t_middle, t_end)  # Concatenate lines.
            ].transpose()  # tunnel_indices[axis, index]
            tunnel_indices = np.append(tunnel_indices, tunnel_indices - 1, axis=1)  # Make tunnels 2 wide.
            gm.tiles[tuple(tunnel_indices)] = engine.tiles.FLOOR
            engine.rendering.debug_map(gm)
        rooms.append(new_room)

    # Start of Water generation:
    # step 1 make random map noise:
    randomMap = create_noise_map(width, height, 80)

    # step 2: feed to cellular automata sevewral times (number of times based on tweaking.
    automataMap1 = convolve(randomMap, 10)  # second value is the number of nearby tiles needed to be water.

    # step 3: Use map to replace wall and floor tiles with water.
    gm.tiles[~automataMap1] = waterType
    engine.rendering.debug_map(gm)

    # Add actors to rooms.
    for room in rooms[1:-1]:
        if random.randint(0, 1):
            # gm.add_actor(engine.actor.Actor(*room.center)) #placeholder enemies.
            gm.add_actor(engine.actor.ColdBoltEnemy(*room.center))
        else:
            gm.add_actor(engine.actor.HunterEnemy(*room.center))
        engine.rendering.debug_map(gm)

    # Add player to the first room.
    if hasattr(model, "map") and model.player in model.map.actors:
        model.map.remove_actor(model.player)  # Remove player from the previous map.
    model.player.x, model.player.y = rooms[0].center
    gm.add_actor(model.player)
    engine.rendering.debug_map(gm)

    gm.add_feature(engine.features.StairsDown(*rooms[-1].center))
    gm.tiles[rooms[-1].center] = engine.tiles.FLOOR
    engine.rendering.debug_map(gm)

    return gm
