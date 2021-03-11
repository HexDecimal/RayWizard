"""World class module."""
from __future__ import annotations

import logging
import random
from typing import List, Optional

import numpy as np

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
            engine.spells.PlaceActor(name="Place bomb", cooldown=8, spawn=engine.actor.Bomb),
            engine.spells.Beam(name="Ice beam", cooldown=3, effect=engine.effects.Cold(power=2)),
            engine.spells.Beam(name="Heat beam", cooldown=8, effect=engine.effects.Heat(power=5)),
            engine.spells.PlaceActor(name="Place totem", cooldown=8, spawn=engine.actor.Totem),
            engine.spells.Blast(name="Heat blast", cooldown=8, effect=engine.effects.Heat(), range=5),
            engine.spells.PlaceActor(name="Seeking bomb", cooldown=12, spawn=engine.actor.FlyingBomb),
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
            if next_obj is self.player:
                # Player remembers visible tiles.
                map_tiles = engine.rendering.render_map(self.map, world_view=None, fullbright=True)
                map_tiles["fg"] //= 4
                map_tiles["bg"] //= 4
                np.putmask(self.map.memory, self.player.get_fov(), map_tiles)
            next_obj.on_turn()
            if self.map.schedule and self.map.schedule[0] is next_obj:
                self.map.schedule.rotate(1)
                # All end-of-turn effects.
                if isinstance(next_obj, engine.actor.Actor):
                    # Apply tile to the actor.
                    tile_effect: Optional[engine.effects.Effect] = self.map.tiles["effect"][next_obj.xy]
                    if tile_effect:
                        tile_effect.apply(*next_obj.xy)
                if next_obj is self.player:
                    # End of player's turn.
                    for spell in self.spell_slots:
                        if spell is None:
                            continue
                        if spell.cooldown_left:
                            spell.cooldown_left -= 1
        logger.info("Player is dead or missing!")
