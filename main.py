#!/usr/bin/env python3
"""Main module.

Run this module from Python to start this program.
"""
from __future__ import annotations  # This may be required to resolve import order issues.

import logging
import os
import sys
import warnings

import tcod

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from engine.state import State  # Import-time requirement, so `from x import Y` is used.
import engine.world
import g
import procgen.dungeon


def main() -> None:
    """Main entrypoint."""
    tileset = tcod.tileset.load_tilesheet("Alloy_curses_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    with tcod.context.new(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, tileset=tileset, title="RayWizard") as g.context:
        # call main menu function here?
        level = 1
        if __debug__:
            level = int(os.environ.get("LEVEL", level))

        while True:
            g.world = engine.world.World()
            g.world.map = procgen.dungeon.generate(g.world, level=level)
            g.world.loop()


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Enable all runtime warnings.
    logging.basicConfig(level=logging.INFO)
    main()


# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]


class MainMenu(State):
    """Handle the main menu rendering and input."""

    def on_draw(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOMBS OF THE ANCIENT KINGS",
            fg=(255, 255, 63),
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By (Your name here)",
            fg=(255, 255, 63),
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=(255, 255, 255),
                bg=(0, 0, 0),
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

        # states.InGame
        return None
