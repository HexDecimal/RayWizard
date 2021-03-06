"""A module for abstract state handling classes.

This module should have as few of its own dependencies as possible.
"""
from __future__ import annotations

import tcod

import g


class State(tcod.event.EventDispatch[None]):
    def on_draw(self, console: tcod.console.Console) -> None:
        """Called when this state should be rendered."""

    def on_escape(self) -> None:
        """By default this will exit out of the current state."""
        assert g.states[-1] is self
        g.states.pop()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_escape()

    def ev_quit(self, event: tcod.event.Quit) -> None:
        raise SystemExit()
