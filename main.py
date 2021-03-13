#!/usr/bin/env python3
"""Main module.

Run this module from Python to start this program.
"""
from __future__ import annotations  # This may be required to resolve import order issues.

import atexit
import logging
import os
import sys
import warnings

import pygame
from pygame import mixer
import tcod

import engine.world
import g
import procgen.dungeon
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


def main() -> None:
    """Main entrypoint."""
    # Prevent Pygame key repeat interference.
    pygame.display.init()
    pygame.display.quit()

    pygame.mixer.init()
    atexit.register(pygame.mixer.quit)

    tileset = tcod.tileset.load_tilesheet("Alloy_curses_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    with tcod.context.new(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, tileset=tileset, title="RayWizard") as g.context:
        level = 1
        pygame.mixer.init()#Initialize music library.
        if __debug__:
            level = int(os.environ.get("LEVEL", level))

        while True:
            # Loading the audio file
            pygame.mixer.music.load('7DRL2--HighTyrol.wav')
            # Playing the Audio file
            mixer.music.play(-1)

            g.world = engine.world.World()
            g.world.map = procgen.dungeon.generate(g.world, level=level)
            g.world.loop()


if __name__ == "__main__":
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Enable all runtime warnings.
    logging.basicConfig(level=logging.INFO)
    main()
