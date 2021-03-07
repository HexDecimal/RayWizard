"""A module for abstract state handling classes.

This module should have as few of its own dependencies as possible.
"""
from __future__ import annotations

import tcod

import g
from constants import CONSOLE_HEIGHT, CONSOLE_WIDTH

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    tcod.event.K_PERIOD: (0, 0),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_5: (0, 0),
    tcod.event.K_CLEAR: (0, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

HOTBAR_KEYS = {
    tcod.event.K_1: 0,
    tcod.event.K_2: 1,
    tcod.event.K_3: 2,
    tcod.event.K_4: 3,
    tcod.event.K_5: 4,
    tcod.event.K_6: 5,
    tcod.event.K_7: 6,
    tcod.event.K_8: 7,
    tcod.event.K_9: 8,
    tcod.event.K_0: 9,  # Zero key means slot 10.
}


class State(tcod.event.EventDispatch[None]):
    """An abstract state.  Subclasses should be made of this class to handle state."""

    def run_modal(self) -> None:
        """Run this state in a modal loop.

        This state takes effect and this function doesn't return until the state is removed from g.states.
        """
        assert self not in g.states
        g.states.append(self)
        while self in g.states:
            # Rendering.
            console = tcod.console.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order="F")
            if __debug__:
                console.clear(bg=(0xFF, 0x00, 0xFF))  # Unhandled areas are now magic pink.
            g.states[-1].on_draw(console)
            g.context.present(console, integer_scaling=True)
            if self not in g.states:
                return
            # Handle input.
            for event in tcod.event.wait():
                g.states[-1].dispatch(event)
                if self not in g.states:
                    return

    def on_draw(self, console: tcod.console.Console) -> None:
        """Called when this state should be rendered.

        `console` will be cleared and drawn by the caller.
        """

    def cmd_cancel(self) -> None:
        """By default this will exit out of the current state."""
        assert g.states[-1] is self
        g.states.pop()

    def cmd_move(self, x: int, y: int) -> None:
        """Movement command.

        `x` and `y` are a direction which may also be `0,0`.
        """

    def cmd_cast(self, index: int) -> None:
        """Cast a spell from the hotbar."""

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        """Dispatch keys to various commands.  This creates a consistant interface across states."""
        if event.sym == tcod.event.K_ESCAPE:
            self.cmd_cancel()
        elif event.sym in MOVE_KEYS:
            self.cmd_move(*MOVE_KEYS[event.sym])
        elif event.sym in HOTBAR_KEYS:
            self.cmd_cast(HOTBAR_KEYS[event.sym])

    def ev_quit(self, event: tcod.event.Quit) -> None:
        """Exit the program a quickly as possible."""
        raise SystemExit()
