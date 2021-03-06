from __future__ import annotations

import tcod

from engine.state import State  # Import-time requirement, so `from x import Y` is used.


class HelloWorld(State):
    def on_draw(self, console: tcod.console.Console) -> None:
        console.print(0, 0, "Hello World")
