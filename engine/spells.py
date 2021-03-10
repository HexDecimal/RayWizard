"""The collection of player spells."""
from __future__ import annotations

from typing import Any, Type

import engine.actions
import engine.actor
import engine.effects


class Spell:
    def __init__(self, *, name: str):
        self.name = name

    def cast(self, actor: engine.actor.Actor) -> bool:
        raise NotImplementedError("Must be overridden.")


class PlaceActor(Spell):
    def __init__(self, *, spawn: Type[engine.actor.Actor], **kargs: Any):
        self.spawn = spawn
        super().__init__(**kargs)

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.PlaceActor(actor, spawn=self.spawn).perform()


class Beam(Spell):
    def __init__(self, *, effect: engine.effects.Effect, **kargs: Any):
        self.effect = effect
        super().__init__(**kargs)

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.Beam(actor, effect=self.effect).perform()


class Blast(Spell):
    def __init__(self, *, effect: engine.effects.Effect, range: int, **kargs: Any):
        self.effect = effect
        self.range = range
        super().__init__(**kargs)

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.Blast(actor, effect=self.effect, range=self.range).perform()
