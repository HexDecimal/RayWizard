"""Actor class module"""
from __future__ import annotations


class Actor:
    """Objects which are able to move on their own."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
