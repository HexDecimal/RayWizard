"""Shorthand globals module.  For sharing mutable objects across modules.

This is for organization and has no special effects.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import tcod

if TYPE_CHECKING:
    import engine.state
    import engine.world

context: tcod.context.Context  # The active context.
states: List[engine.state.State] = []  # A stack of states, with the last item being the active state.
world: engine.world.World  # The active world.

debug_dungeon_generation: bool = __debug__  # Visualize the dungeon being generated.
debug_fullbright: bool = False
debug_rendering: bool = False  # Highlight areas which have not been drawn over.
