"""Event scheduler module.
"""


class Schedulable:
    skip_turns: int = 0

    def on_turn(self) -> None:
        pass
