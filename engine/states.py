"""Game states module."""
from __future__ import annotations

from typing import Optional, Tuple

import tcod

import engine.actions
import engine.rendering
import g
from engine.state import State  # Import-time requirement, so `from x import Y` is used.


class HelloWorld(State):
    """Testing hello world class."""

    def on_draw(self, console: tcod.console.Console) -> None:
        console.print(0, 0, "Hello World")


class InGame(State):
    """The normal in-game state.  Where the player has control over their own actor object."""

    def on_draw(self, console: tcod.console.Console) -> None:
        engine.rendering.render_main(console)

    def cmd_move(self, x: int, y: int) -> None:
        if engine.actions.MoveAction(g.world.player, (x, y)).perform():
            g.states.pop()  # Return control to World.loop.

    def cmd_cast(self, index: int) -> None:
        """Cast a spell from the hotbar."""
        spell = g.world.spell_slots[index]
        g.world.report(f"You cast {spell}")
        if spell and spell(g.world.player).perform():
            g.states.pop()


class AskDirection(State):
    direction: Optional[Tuple[int, int]] = None

    def on_draw(self, console: tcod.console.Console) -> None:
        engine.rendering.render_main(console)
        engine.rendering.print_extra_text(console, "Pick a direction...")

    def cmd_move(self, x: int, y: int) -> None:
        self.direction = (x, y)
        g.states.pop()
