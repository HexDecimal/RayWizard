"""Game states module."""
from __future__ import annotations

import tcod

import engine.actions
import g
from engine.state import State  # Import-time requirement, so `from x import Y` is used.


class HelloWorld(State):
    """Testing hello world class."""

    def on_draw(self, console: tcod.console.Console) -> None:
        console.print(0, 0, "Hello World")


class InGame(State):
    """The normal in-game state.  Where the player has control over their own actor object."""

    def on_draw(self, console: tcod.console.Console) -> None:
        # Mostly example code.
        map_ = g.world.map
        UI_SIZE = (12, 12)  # Area reserved for the UI.
        console_shape = (console.width - UI_SIZE[0], console.height - UI_SIZE[1])
        console.tiles_rgb[: console_shape[0], : console_shape[1]] = ord(" "), 0x40, 0x00  # Clear world area.
        screen_view, world_view = map_.camera.get_views((map_.width, map_.height), console_shape)
        console.tiles_rgb["ch"][screen_view] = g.world.map.tiles["ch"][world_view]
        cam_x, cam_y = map_.camera.get_left_top_pos(console_shape)
        for actor in g.world.map.actors:  # Render all actors.
            x = actor.x - cam_x
            y = actor.y - cam_y
            if 0 <= x < console_shape[0] and 0 <= y < console_shape[1]:
                console.print(x, y, "@", fg=(0xFF, 0xFF, 0xFF))

    def cmd_move(self, x: int, y: int) -> None:
        if engine.actions.MoveAction(g.world.player, (x, y)).perform():
            g.states.pop()  # Return control to World.loop.
