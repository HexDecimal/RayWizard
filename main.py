#!/usr/bin/env python3
"""Main module.

Run this module from Python to start this program.
"""
import sys
import warnings

import tcod

import g

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

CONSOLE_WIDTH = SCREEN_WIDTH // 12
CONSOLE_HEIGHT = SCREEN_HEIGHT // 12


def main() -> None:
    """Main entrypoint."""
    tileset = tcod.tileset.load_tilesheet("Alloy_curses_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    with tcod.context.new(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, tileset=tileset) as g.context:
        while True:
            # Rendering.
            console = tcod.console.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order="C")
            console.print(0, 0, "Hello World")
            g.context.present(console, integer_scaling=True)
            # Handle input.
            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Enable all runtime warnings.
    main()
