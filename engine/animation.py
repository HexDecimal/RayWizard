from __future__ import annotations

import engine.rendering
import g
from constants import CONSOLE_HEIGHT, CONSOLE_WIDTH


class Animation:
    """Show the world when between player turns."""

    def show(self) -> None:
        console = g.context.new_console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order="F")
        engine.rendering.render_main(console)
        g.context.present(console, integer_scaling=True)
