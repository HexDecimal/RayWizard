"""Rendering functions."""
from __future__ import annotations

from typing import Tuple

import numpy as np
import tcod

import engine.map
import g

UI_SIZE = (12, 12)  # Area reserved for the UI.

SHROUD = np.asarray((ord(" "), (0x40, 0x40, 0x40), (0x00, 0x00, 0x00)), dtype=engine.map.tile_graphic)
"The clear graphic before drawing world tiles."


def render_tiles(shape: Tuple[int, int]) -> np.ndarray:
    """Return a Console.tilese_rgb compatiable array of world tiles.

    `shape` is the (width, height) of the returned array.

    This array is in Fortran order and is centered over the world camera.
    """
    map_ = g.world.map
    output = np.full(shape, SHROUD, order="F")
    screen_view, world_view = g.world.map.camera.get_views((map_.width, map_.height), shape)
    output[screen_view] = map_.tiles["dark"][world_view]
    return output


def render_main(console: tcod.console.Console) -> None:
    """Rendeer the main view.  With the world tiles, any objects, and the UI."""
    # Render world tiles.
    console_shape = (console.width - UI_SIZE[0], console.height - UI_SIZE[1])
    console.tiles_rgb[: console_shape[0], : console_shape[1]] = render_tiles(console_shape)

    # Render all actors.
    cam_x, cam_y = g.world.map.camera.get_left_top_pos(console_shape)
    for actor in g.world.map.actors:
        x = actor.x - cam_x
        y = actor.y - cam_y
        if 0 <= x < console_shape[0] and 0 <= y < console_shape[1]:
            console.print(x, y, actor.ch, fg=actor.fg)
