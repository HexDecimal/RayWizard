"""Rendering functions."""
from __future__ import annotations

from typing import Tuple

import numpy as np
import tcod

import g
from engine.tiles import tile_graphic

UI_SIZE = (24, 12)  # Area reserved for the UI.

SHROUD = np.asarray((ord(" "), (0x40, 0x40, 0x40), (0x00, 0x00, 0x00)), dtype=tile_graphic)
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


FG = (0xFF, 0xFF, 0xFF)
BG = (0, 0, 0)


def render_slots(console: tcod.console.Console) -> None:
    """Render the spell slots UI."""
    x = console.width - UI_SIZE[0] + 1
    console.tiles_rgb[x - 1, :] = ord("▒"), FG, BG
    for i, spell in enumerate(g.world.spell_slots):
        spell_name = "--------" if spell is None else spell.__name__
        spell_console = tcod.console.Console(UI_SIZE[0] - 1, 6, order="F")
        spell_console.print(0, 0, f"{i+1:2d}. {spell_name}", fg=FG, bg=BG)
        spell_console.print(spell_console.width - 3, spell_console.height - 1, "^^^", fg=FG, bg=BG)

        spell_console.blit(console, x, i * 6)


def render_log(log_console: tcod.console.Console) -> None:
    """Render the log to a dedicated console."""
    y = log_console.height
    for message in reversed(g.world.log):
        y -= tcod.console.get_height_rect(log_console.width, message)
        log_console.print_box(0, y, 0, 0, message, fg=FG, bg=BG)


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

    render_slots(console)

    console.tiles_rgb[: -UI_SIZE[0], -UI_SIZE[1]] = 0x2592, FG, BG
    log_console = tcod.Console(console.width - UI_SIZE[0], UI_SIZE[1] - 1)
    render_log(log_console)
    log_console.blit(console, 0, console.height - UI_SIZE[1] + 1)


def print_extra_text(console: tcod.console.Console, message: str) -> None:
    """Prints extra temporary text.

    I'm not sure how this should be handled.
    """
    console.print(0, console.height - UI_SIZE[1] - 1, message, fg=FG, bg=BG)
