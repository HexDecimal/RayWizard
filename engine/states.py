"""Game states module."""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import tcod

from engine.state import State  # Import-time requirement, so `from x import Y` is used.
import engine.actions
import engine.rendering
import g
import procgen.dungeon


class HelloWorld(State):
    """Testing hello world class."""

    def on_draw(self, console: tcod.console.Console) -> None:
        console.print(0, 0, "Hello World")


HELP_TEXT = """\
To move around use the number pad keys, VI keys, or the arrow keys along with home/end/pageup/pagedown.

 7 8 9  y k u
 4 5 6  h . l
 1 2 3  b j n

The period key [.] or [keypad 5] can be used to wait a turn.

The standard numbers [0]..[9] are used to select spells.

[x] Auto-explore.
[esc] Exit this screen and cancel out of other actions.
[?] Show this screen.
"""


class Help(State):
    def on_draw(self, console: tcod.console.Console) -> None:
        engine.rendering.render_main(console)
        console.tiles_rgb["fg"] //= 16
        console.tiles_rgb["bg"] //= 16
        width, height = 60, 32

        console.print_box(
            (console.width - width) // 2,
            (console.height - height) // 2,
            width,
            height,
            HELP_TEXT,
            fg=engine.rendering.TEXT_COLOR,
            bg=None,
        )


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

    def cmd_down(self) -> None:
        for obj in g.world.map.features:
            if not (obj.x == g.world.player.x and obj.y == g.world.player.y):
                continue
            if not isinstance(obj, engine.features.StairsDown):
                continue
            g.world.player.hp = 12
            if g.world.map.level + 1 != 4:
                g.world.map = procgen.dungeon.generate(g.world, level=g.world.map.level + 1)
            else:
                WinScreen().run_modal()  # logic for the end of the game.
            g.states.pop()
            break

    def cmd_help(self) -> None:
        Help().run_modal()

    def cmd_cancel(self) -> None:
        EscapeMenu().run_modal()

    def cmd_explore(self) -> None:
        g.world.player.ai = engine.actions.AutoExplore(g.world.player)
        g.states.pop()

    def debug_regenerate_map(self) -> None:
        g.world.map = procgen.dungeon.generate(g.world, level=g.world.map.level)
        g.states.pop()  # Reset the players turn.


class AskDirection(State):
    direction: Optional[Tuple[int, int]] = None

    def __init__(self, can_target_self: bool = True):
        super().__init__()
        self.can_target_self = can_target_self

    def on_draw(self, console: tcod.console.Console) -> None:
        highlight = np.zeros_like(g.world.map.tiles, dtype=bool)
        highlight[g.world.player.x - 1 :, g.world.player.y - 1 :][:3, :3] = True
        if not self.can_target_self:
            highlight[g.world.player.x, g.world.player.y] = False
        engine.rendering.render_main(console, visible_callbacks=[engine.rendering.Highlight(highlight)])
        engine.rendering.print_extra_text(console, "Pick a direction...")

    def cmd_move(self, x: int, y: int) -> None:
        self.direction = (x, y)
        g.states.pop()


class KillScreen(State):
    """Displayed on the players death."""

    def on_draw(self, console: tcod.console.Console) -> None:
        engine.rendering.render_main(console)


WIN_TEXT = """\
Congradulations!

You have escaped your dungeon prison, and Won the Game!
Now you roam the planet, with your newfound freedom!
"""


class WinScreen(State):
    """Screen for winning the game."""

    def on_draw(self, console: tcod.console.Console) -> None:
        console.clear()
        width, height = 60, 32

        console.print_box(
            (console.width - width) // 2,
            (console.height - height) // 2,
            width,
            height,
            WIN_TEXT,
            fg=engine.rendering.TEXT_COLOR,
            bg=None,
        )

    def cmd_cancel(self) -> None:
        raise SystemExit()


class EscapeMenu(State):
    def __init__(self) -> None:
        super().__init__()
        self.cursor = 0
        self.menu = (
            ("Return to game", self.cmd_cancel),
            ("Quit", self.quit),
        )

    def on_draw(self, console: tcod.console.Console) -> None:
        engine.rendering.render_main(console)
        console.tiles_rgb["fg"] //= 12
        console.tiles_rgb["bg"] //= 12
        width, height = 30, 8
        left = (console.width - width) // 2
        top = (console.height - height) // 2

        for i, (text, _) in enumerate(self.menu):
            fg = engine.rendering.TEXT_COLOR
            bg = None
            if i == self.cursor:
                bg = engine.rendering.TEXT_COLOR
                fg = engine.rendering.BLACK
            console.print(left, top + i, text, fg=fg, bg=bg)

    def cmd_move(self, x: int, y: int) -> None:
        if x:
            return
        self.cursor = (self.cursor + y) % len(self.menu)
        if y == 0:
            self.cmd_confirm()

    def cmd_confirm(self) -> None:
        self.menu[self.cursor][1]()

    def quit(self) -> None:
        raise SystemExit()
