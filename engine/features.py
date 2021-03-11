from __future__ import annotations


class Feature:
    ch = ord("?")
    fg = (0xFF, 0xFF, 0xFF)

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class StairsDown(Feature):
    ch = ord(">")
