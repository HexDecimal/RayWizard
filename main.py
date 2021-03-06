#!/usr/bin/env python3
"""Main module.

Run this module from Python to start this program.
"""
from __future__ import annotations  # This may be required to resolve import order issues.

import sys
import warnings

import tcod

import engine.states
import g

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

CONSOLE_WIDTH = SCREEN_WIDTH // 12
CONSOLE_HEIGHT = SCREEN_HEIGHT // 12


def main() -> None:
    """Main entrypoint."""
    tileset = tcod.tileset.load_tilesheet("Alloy_curses_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    with tcod.context.new(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, tileset=tileset) as g.context:
        g.states = [engine.states.HelloWorld()]
        while g.states:
            # Rendering.
            console = tcod.console.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order="C")
            g.states[-1].on_draw(console)
            g.context.present(console, integer_scaling=True)
            # Handle input.
            for event in tcod.event.wait():
                if g.states:
                    g.states[-1].dispatch(event)


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Enable all runtime warnings.
    main()
