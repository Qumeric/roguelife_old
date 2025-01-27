from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any

from numpy.typing import NDArray
from tcod.console import Console
import numpy as np

from entity import Actor, Building, Item
from events import SpawnEvent, spawn_signal
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def visible(self) -> NDArray[Any]:
        return self.engine.player.visible

    @property
    def explored(self) -> NDArray[Any]:
        return self.engine.player.explored

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (entity for entity in self.entities if isinstance(entity, Actor) and entity.is_alive)

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    @property
    def buildings(self) -> Iterator[Building]:
        yield from (entity for entity in self.entities if isinstance(entity, Building))

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Entity | None:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Actor | None:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def get_building_at_location(self, x: int, y: int) -> Building | None:
        for building in self.buildings:
            if building.x == x and building.y == y:
                return building

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities_sorted_for_rendering:
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)

    def can_spawn_at(self, x: int, y: int) -> bool:
        """Return True if an entity can spawn at this location."""
        return self.in_bounds(x, y) and not self.get_blocking_entity_at_location(x, y)

    def spawn(self, entity: Entity) -> None:
        entity.parent = self
        self.entities.add(entity)

        spawn_signal.send(
            self,
            event=SpawnEvent(entity.x, entity.y, entity),
        )

    def get_entities_at_location(self, x: int, y: int) -> list[Entity]:
        return [entity for entity in self.entities if entity.x == x and entity.y == y]

    def get_names_at_location(self, x: int, y: int) -> str:
        if not self.in_bounds(x, y) or not self.visible[x, y]:
            return ""

        entities = self.get_entities_at_location(x, y)
        names = ", ".join(map(lambda entity: entity.name, entities))

        return names.capitalize()

    def get_neighbors(self, x: int, y: int):
        neighbors = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        valid_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.width and 0 <= ny < self.height]
        return valid_neighbors
