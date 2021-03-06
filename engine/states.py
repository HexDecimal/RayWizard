"""Game states module."""
from __future__ import annotations

import tcod

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
        console.tiles_rgb["ch"] = g.world.map.tiles["ch"][: console.width, : console.height]
        console.tiles_rgb["fg"] = 0x40  # Darken these tiles.
        for actor in g.world.map.actors:  # Render all actors.
            if 0 <= actor.x < console.width and 0 <= actor.y < console.height:
                console.print(actor.x, actor.y, "@", fg=(0xFF, 0xFF, 0xFF))

    def cmd_move(self, x: int, y: int) -> None:
        # Test example.
        x = g.world.player.x + x
        y = g.world.player.y + y
        if g.world.map.is_not_blocked(x, y):
            g.world.player.x = x
            g.world.player.y = y
