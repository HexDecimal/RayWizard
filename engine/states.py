"""Game states module."""
from __future__ import annotations

from typing import Optional, Tuple

import tcod

import engine.actions
import engine.rendering
import g
import procgen.dungeon
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
        if not spell:
            return
        if spell.cooldown_left:
            g.world.report(f"{spell.name} is on cooldown!")
            return
        g.world.report(f"You cast {spell.name}")
        if spell.cast(g.world.player):
            spell.cooldown_left = spell.cooldown_length + 1
            g.states.pop()

    def debug_regenerate_map(self) -> None:
        g.world.map = procgen.dungeon.generate(g.world)
        g.states.pop()  # Reset the players turn.


class AskDirection(State):
    direction: Optional[Tuple[int, int]] = None

    def on_draw(self, console: tcod.console.Console) -> None:
        engine.rendering.render_main(console)
        engine.rendering.print_extra_text(console, "Pick a direction...")

    def cmd_move(self, x: int, y: int) -> None:
        self.direction = (x, y)
        g.states.pop()
