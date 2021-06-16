"""Animation system.

Handles rendering frames between player actions.
"""
from __future__ import annotations

from typing import Sequence
import time

import tcod

from constants import CONSOLE_HEIGHT, CONSOLE_WIDTH
import engine.rendering
import g


def events_in_queue() -> bool:
    """Returns True if important events are waiting on the queue."""
    tcod.lib.SDL_PumpEvents()
    return bool(
        tcod.lib.SDL_HasEvent(tcod.lib.SDL_KEYDOWN)
        or tcod.lib.SDL_HasEvent(tcod.lib.SDL_MOUSEBUTTONDOWN)
        or tcod.lib.SDL_HasEvent(tcod.lib.SDL_QUIT)
    )


class Animation:
    """Show the world when between player turns.

    `layers` are the extra graphics to show, such as a bullet sprite.

    `sleep_time` is the time to sleep after the frame is presented.
    """

    def __init__(self, layers: Sequence[engine.rendering.Layer] = (), sleep_time: float = 1 / 40):
        self.layers = layers
        self.sleep_time = sleep_time

    def show(self) -> None:
        """Show this animation.  Presents a single frame."""
        console = g.context.new_console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order="F")
        engine.rendering.render_main(console, visible_callbacks=self.layers)
        g.context.present(console, integer_scaling=True)
        if not events_in_queue():  # Fast-forward if an important event is on the queue.
            # This could be improved with a good way to reference the last time a frame was drawn.
            # Until then this sleeps `sleep_time` time on top of how much time has already passed.
            time.sleep(self.sleep_time)
