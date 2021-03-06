"""Shorthand globals module.  For sharing mutable objects across modules.

This is for organization and has no special effects.
"""
from __future__ import annotations

from typing import List

import tcod

import engine.state

context: tcod.context.Context  # Global context
states: List[engine.state.State] = []
