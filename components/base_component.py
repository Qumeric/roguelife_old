from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.observation_log import ObservationLog
    from engine import Engine
    from entity import Actor, Entity
    from game_map import GameMap


class BaseComponent(ABC):
    parent: Entity  # Owning entity instance.

    @abstractmethod
    def update(self) -> None:
        """Perform any logic that needs to happen on this component's turn."""

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
