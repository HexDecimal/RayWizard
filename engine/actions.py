"""Collections of actions."""
from __future__ import annotations

from typing import Any, Optional, Tuple

import engine.actor
import engine.states
import g


class Action:
    """Basic action with no targets other than the invoking actor."""

    def __init__(self, actor: engine.actor.Actor):
        super().__init__()
        self.actor = actor  # The actor performing this action.

    def perform(self) -> bool:
        """Perform the action and return its status.

        If True then this action took time to perform and will end the actors turn.
        """
        return True


class ActionWithDir(Action):
    """An action with a direction."""

    def __init__(self, actor: engine.actor.Actor, direction: Optional[Tuple[int, int]], **kargs: Any):
        super().__init__(actor=actor, **kargs)  # type: ignore
        self._direction = direction

    @property
    def direction(self) -> Tuple[int, int]:
        """The direction of this action."""
        if not self._direction:
            assert self.actor is g.world.player
            state = engine.states.AskDirection()
            state.run_modal()
            self._direction = state.direction
            assert self._direction  # Todo, handle no direction given.
        return self._direction

    @property
    def target_xy(self) -> Tuple[int, int]:
        """The target position immediately in front of this action."""
        return self.actor.x + self.direction[0], self.actor.y + self.direction[1]


class IdleAction(Action):
    """Do nothing and pass a turn."""


class MoveAction(ActionWithDir):
    """Move an actor normally."""

    def perform(self) -> bool:
        if self.direction == (0, 0):
            return IdleAction(self.actor).perform()
        xy = self.target_xy
        if g.world.map.is_not_blocked(*xy):
            self.actor.x, self.actor.y = xy
            return True
        return False


class PlaceBomb(ActionWithDir):
    """Place bomb, pratice action."""

    def perform(self) -> bool:
        xy = self.target_xy
        if g.world.map.is_not_blocked(*xy):
            g.world.map.add_actor(engine.actor.Bomb(*xy))
            return True
        return False
