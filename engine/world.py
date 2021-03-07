"""World class module."""
from __future__ import annotations

import logging
import random
from typing import List, Optional

import engine.actions
import engine.actor
import engine.map
import engine.spells

logger = logging.getLogger(__name__)


class World:
    """This class is used to hold everything you'll want to save between sessions."""

    player: engine.actor.Actor  # The active player actor, this might be removed from here.

    def __init__(self) -> None:
        self.map = engine.map.Map(128, 128)
        self.rng = random.Random()
        self.spell_slots: List[Optional[engine.spells.Spell]] = [
            engine.spells.PlaceActor(name="Place bomb", spawn=engine.actor.Bomb),
            engine.spells.Beam(name="Ice beam", effect=engine.effects.Cold()),
            engine.spells.Beam(name="Heat beam", effect=engine.effects.Heat()),
            engine.spells.PlaceActor(name="Place totem", spawn=engine.actor.Totem),
            None,
            None,
            None,
            None,
            None,
            None,
        ]  # Spells equipped to the hotbar.
        assert len(self.spell_slots) == 10
        self.log: List[str] = []  # Text log.

    def report(self, message: str) -> None:
        """Append to the text log."""
        logger.info(message)
        self.log.append(message)

    def loop(self) -> None:
        while self.player in self.map.actors:
            next_obj = self.map.schedule[0]
            next_obj.on_turn()
            if self.map.schedule and self.map.schedule[0] is next_obj:
                self.map.schedule.rotate(1)
        logger.info("Player is dead or missing!")
