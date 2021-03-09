"""Collections of actions."""
from __future__ import annotations

import logging
from typing import Any, Iterator, Optional, Tuple, Type

import engine.actor
import engine.effects
import engine.states
import engine.tiles
import g

logger = logging.getLogger(__name__)


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

    def __init__(self, actor: engine.actor.Actor, direction: Optional[Tuple[int, int]] = None, **kargs: Any):
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

    def trace_line(self) -> Iterator[Tuple[int, int]]:
        """Trace a line in the provided direction until out of bounds."""
        x, y = self.actor.x, self.actor.y
        if self.direction == (0, 0):
            yield x, y  # Target self.
            return
        while True:
            x += self.direction[0]
            y += self.direction[1]
            if not g.world.map.in_bounds(x, y):
                break
            yield x, y


class ActionWithEffect(Action):
    def __init__(self, actor: engine.actor.Actor, effect: engine.effects.Effect, **kargs: Any):
        super().__init__(actor=actor, **kargs)  # type: ignore
        self.effect = effect


class IdleAction(Action):
    """Do nothing and pass a turn."""


class MoveAction(ActionWithDir):
    """Move an actor normally."""

    def perform(self) -> bool:
        if self.direction == (0, 0):
            return IdleAction(self.actor).perform()
        xy = self.target_xy
        if not g.world.map.is_blocked(*xy):
            self.actor.x, self.actor.y = xy
            return True
        return False


class PlaceActor(ActionWithDir):
    """Place bomb, pratice action."""

    def __init__(self, actor: engine.actor.Actor, spawn: Type[engine.actor.Actor], **kargs: Any):
        self.spawn = spawn
        super().__init__(actor=actor, **kargs)

    def perform(self) -> bool:
        xy = self.target_xy
        if not g.world.map.is_blocked(*xy):
            g.world.map.add_actor(self.spawn(*xy))
            return True
        return False


class Beam(ActionWithDir, ActionWithEffect):
    def perform(self) -> bool:
        """Trace a line and apply effects along it until a wall is hit."""
        for xy in self.trace_line():
            if not g.world.map.tiles[xy]["transparent"]:
                break  # Hit wall.
            self.effect.apply(*xy)
        return True


class RandomStep(Action):
    """Move in a random direction."""

    def perform(self) -> bool:
        direction = g.world.rng.choice(
            [
                (1, 1),
                (-1, 1),
                (-1, -1),
                (1, -1),
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ]
        )
        return engine.actions.MoveAction(self.actor, direction).perform()


class DefaultAI(Action):
    """Default AI action when None is given to Actor."""

    def perform(self) -> bool:
        return RandomStep(self.actor).perform()


class PlayerControl(Action):
    """Give control to the player."""

    def perform(self) -> bool:
        logger.info("Player turn")
        assert g.world.player is self.actor
        g.world.map.camera = engine.map.Camera(self.actor.x, self.actor.y)
        engine.states.InGame().run_modal()
        return True
