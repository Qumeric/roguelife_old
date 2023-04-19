from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor
    from game_map import GameMap
    from components import ObservationLog


class BaseComponent:
    parent: Entity  # Owning entity instance.

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    @property
    def engine(self) -> Engine:
        return self.game_map.engine


class ActorComponent(BaseComponent):
    parent: Actor

    @property
    def observations(self) -> ObservationLog:
        return self.parent.observation_log
