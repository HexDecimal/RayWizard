"""The collection of player spells."""
from __future__ import annotations

from typing import Any

import engine.actions
import engine.actor
import engine.effects


class Spell:
    def __init__(self, *, name: str):
        self.name = name

    def cast(self, actor: engine.actor.Actor) -> bool:
        raise NotImplementedError("Must be overridden.")


class PlaceBomb(Spell):
    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.PlaceBomb(actor).perform()


class Beam(Spell):
    def __init__(self, *, effect: engine.effects.Effect, **kargs: Any):
        self.effect = effect
        super().__init__(**kargs)

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.Beam(actor, effect=self.effect).perform()
