"""The collection of player spells."""
from __future__ import annotations

from typing import Any, Optional, Type
import warnings

import engine.actions
import engine.actor
import engine.effects


class Spell:
    desc = "Spell desc"

    def __init__(self, *, name: str, cooldown: int, desc: Optional[str] = None):
        self.name = name
        self.cooldown_length = cooldown
        self.cooldown_left = 0
        if self.desc == Spell.desc:
            warnings.warn(f"{self.name} is missing a description.")
        self.desc = desc if desc is not None else self.generate_desc()

    def generate_desc(self) -> str:
        """Generate a description."""
        return self.desc

    def cast(self, actor: engine.actor.Actor) -> bool:
        raise NotImplementedError("Must be overridden.")


class PlaceActor(Spell):
    def __init__(self, *, spawn: Type[engine.actor.Actor], **kargs: Any):
        self.spawn = spawn
        super().__init__(**kargs)

    def generate_desc(self) -> str:
        return f"Create a new {self.spawn.name} nearby."

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.PlaceActor(actor, spawn=self.spawn).perform()


class Beam(Spell):
    def __init__(self, *, effect: engine.effects.Effect, **kargs: Any):
        self.effect = effect
        super().__init__(**kargs)

    def generate_desc(self) -> str:
        return f"Fire a concentrated beam of {self.effect.name}."

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.Beam(actor, effect=self.effect).perform()


class Blast(Spell):
    def __init__(self, *, effect: engine.effects.Effect, range: int, **kargs: Any):
        self.effect = effect
        self.range = range
        super().__init__(**kargs)

    def generate_desc(self) -> str:
        return f"Create a wave of {self.effect.name} from the caster.\nRange {self.range}."

    def cast(self, actor: engine.actor.Actor) -> bool:
        return engine.actions.Blast(actor, effect=self.effect, range=self.range).perform()


class EarthVision(Spell):
    desc = "Reveals areas behind walls."

    def __init__(self, *, length: int, **kargs: Any):
        self.length = length
        super().__init__(**kargs)

    def cast(self, actor: engine.actor.Actor) -> bool:
        actor.status["earth vision"] = self.length
        return True
