"""Rendering functions."""
from __future__ import annotations

from typing import Iterable, Optional, Tuple
import time

import numpy as np
import tcod

from engine.tiles import tile_graphic
import engine.map
import g

UI_SIZE = (24, 12)  # Area reserved for the UI.

SHROUD = np.asarray((ord(" "), (0x40, 0x40, 0x40), (0x00, 0x00, 0x00)), dtype=tile_graphic)
"The clear graphic before drawing world tiles."


class Layer:
    """Post process rendering callback."""

    def render(self, output: np.ndarray, world_view: Tuple[slice, slice]) -> None:
        raise NotImplementedError()


class Highlight(Layer):
    """Highlight specific tiles."""

    def __init__(self, highlight: np.ndarray):
        assert highlight.dtype == bool
        self.highlight = highlight

    def render(self, output: np.ndarray, world_view: Tuple[slice, slice]) -> None:
        np.invert(output["bg"], out=output["bg"], where=self.highlight[world_view][..., np.newaxis])
        np.invert(output["fg"], out=output["fg"], where=self.highlight[world_view][..., np.newaxis])


class Sprite(Layer):
    """Apply a single sprite to the world."""

    def __init__(self, x: int, y: int, ch: int, fg: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.ch = ch
        self.fg = fg

    def render(self, output: np.ndarray, world_view: Tuple[slice, slice]) -> None:
        if not (
            world_view[0].start <= self.x < world_view[0].stop and world_view[1].start <= self.y < world_view[1].stop
        ):
            return
        x = self.x - world_view[0].start
        y = self.y - world_view[1].start
        output[["ch", "fg"]][x, y] = self.ch, self.fg


def render_map(
    map_: engine.map.Map,
    world_view: Optional[Tuple[slice, slice]],
    fullbright: bool = True,
    visible_callbacks: Iterable[Layer] = (),
) -> np.ndarray:
    """Return a Console.tilese_rgb compatiable array of the map.

    `map_` is the Map object to render.

    `shape` is the (width, height) of the returned array.

    If `fullbright` is True then everything is visbile, otherwise the player FOV is used.

    This is a full rendering of the map, including any objects.
    """
    if not world_view:
        world_view = slice(0, map_.width), slice(0, map_.height)
    output: np.ndarray = map_.tiles["graphic"][world_view].copy()

    cam_x, cam_y = world_view[0].start, world_view[1].start
    # Render features.
    for feature in map_.features:
        x = feature.x - cam_x
        y = feature.y - cam_y
        if 0 <= x < output.shape[0] and 0 <= y < output.shape[1]:
            output[["ch", "fg"]][x, y] = feature.ch, feature.fg
    # Render all actors.
    for actor in map_.actors:
        x = actor.x - cam_x
        y = actor.y - cam_y
        if 0 <= x < output.shape[0] and 0 <= y < output.shape[1]:
            output[["ch", "fg"]][x, y] = ord(actor.ch), actor.fg

    for callback in visible_callbacks:
        callback.render(output, world_view)

    if fullbright:
        return output

    output = np.where(g.world.player.get_fov()[world_view], output, g.world.map.memory[world_view])
    return output


def debug_map(map_: engine.map.Map, sleep_time: float = 0) -> None:
    """Present the current map tiles.  This is ignored on release mode."""
    if not g.debug_dungeon_generation:
        return
    for ev in tcod.event.get():
        if isinstance(ev, tcod.event.KeyDown):
            g.debug_dungeon_generation = False
    g.world.map = map_
    console = tcod.Console(map_.width, map_.height, order="F")
    console.tiles_rgb[:] = render_map(map_, world_view=None, fullbright=True)
    g.context.present(console)
    time.sleep(sleep_time)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = BLACK

BORDER_COLOR = (94, 4, 2)
TEXT_COLOR = WHITE
TEXT_UNIMPORTANT = (128, 128, 128)


def render_slots(console: tcod.console.Console) -> None:
    """Render the spell slots UI."""
    x = console.width - UI_SIZE[0] + 1
    console.tiles_rgb[x - 1, :] = ord("▒"), BORDER_COLOR, BLACK
    for i, spell in enumerate(g.world.spell_slots):
        if spell is None:
            continue  # Skip drawing this slot.
        spell_name = "--------" if spell is None else spell.name
        spell_console = tcod.console.Console(UI_SIZE[0] - 1, 6, order="F")
        spell_console.print(0, 0, f"{i+1:2d}. {spell_name}", fg=TEXT_COLOR, bg=BG)
        if spell is not None:
            spell_console.print(0, 1, f"Cooldown: {spell.cooldown_left}/{spell.cooldown_length}", fg=TEXT_COLOR, bg=BG)
            spell_console.print_box(0, 2, 0, 0, spell.desc, fg=TEXT_UNIMPORTANT, bg=BG)

        spell_console.blit(console, x, i * 6)


def render_log(log_console: tcod.console.Console) -> None:
    """Render the log to a dedicated console."""
    y = log_console.height
    for message in reversed(g.world.log):
        y -= tcod.console.get_height_rect(log_console.width, message)
        if y < 0:
            break
        log_console.print_box(0, y, 0, 0, message, fg=TEXT_COLOR, bg=BG)


def render_main(console: tcod.console.Console, visible_callbacks: Iterable[Layer] = ()) -> None:
    """Rendeer the main view.  With the world tiles, any objects, and the UI."""
    # Render map view.
    console_shape = (console.width - UI_SIZE[0], console.height - UI_SIZE[1])
    screen_view, world_view = g.world.map.camera.get_views(g.world.map.tiles.shape, console_shape)
    console.tiles_rgb[: console_shape[0], : console_shape[1]] = SHROUD
    console.tiles_rgb[screen_view] = render_map(
        g.world.map, world_view, fullbright=g.debug_fullbright, visible_callbacks=visible_callbacks
    )

    render_slots(console)

    STATUS_WIDTH = 20
    console.tiles_rgb[: -UI_SIZE[0], -UI_SIZE[1]] = 0x2592, BORDER_COLOR, BLACK  # Bar along the lower end of the map.
    console.tiles_rgb[-UI_SIZE[0] - STATUS_WIDTH - 1, -UI_SIZE[1] :] = (0x2592, BORDER_COLOR, BLACK)  # log/status bar.

    log_console = tcod.Console(console.width - UI_SIZE[0] - STATUS_WIDTH - 1, UI_SIZE[1] - 1)
    render_log(log_console)
    log_console.blit(console, 0, console.height - UI_SIZE[1] + 1)

    status_console = tcod.Console(STATUS_WIDTH, UI_SIZE[1] - 1)
    status_console.print(0, 0, f"Status - {g.world.player.x},{g.world.player.y}")
    status_console.print(0, 1, f"HP {g.world.player.hp}")
    status_console.print(0, status_console.height - 1, f"Dungeon level {g.world.map.level}")
    status_console.blit(console, console.width - UI_SIZE[0] - STATUS_WIDTH, console.height - UI_SIZE[1] + 1)


def print_extra_text(console: tcod.console.Console, message: str) -> None:
    """Prints extra temporary text.

    I'm not sure how this should be handled.
    """
    console.print(0, console.height - UI_SIZE[1] - 1, message, fg=TEXT_COLOR, bg=BG)


# I want to add a function which renders a main menu whith an option to start a new game or load a save game.
# perhaps inclue help as well
# Ideally it would be extnedable to all things we might want to add to it later.
# And include a nice title.
# Also needs logic in main to start the main game logic after the menu.
# def render_main_menu() -> None:
#

# I want to add an interactive popup renderer? Probably make a popup object as well as the function to render it.
# Might be reusable as a crude main menu?
# The main applications is warning notices for dangerous terrain.
# Pits, lava, detected traps, etc.
