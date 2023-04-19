from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

import entity_factories
from game_map import GameMap
import tile_types


if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1


def place_entities(room: RectangularRoom, dungeon: GameMap, maximum_monsters: int, maximum_items: int) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)
    number_of_items = random.randint(0, maximum_items)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() < 0.8:
                entity_factories.spawn_orc(dungeon, x, y)
            else:
                entity_factories.spawn_troll(dungeon, x, y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            item_chance = random.random()

            if item_chance < 0.7:
                entity_factories.spawn_health_potion(dungeon, x, y)
            elif item_chance < 0.80:
                entity_factories.spawn_fireball_scroll(dungeon, x, y)
            elif item_chance < 0.90:
                entity_factories.spawn_confusion_scroll(dungeon, x, y)
            else:
                entity_factories.spawn_lightning_scroll(dungeon, x, y)


def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    max_monsters_per_room: int,
    max_items_per_room: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        place_entities(new_room, dungeon, max_monsters_per_room, max_items_per_room)

        # Finally, append the new room to the list.
        rooms.append(new_room)

    return dungeon


import numpy as np
import tcod.noise


def generate_heightmap(
    width: int, height: int, scale: float, octaves: int, persistence: float, lacunarity: float
) -> np.ndarray:
    shape = (width, height)

    noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.NOISE_SIMPLEX,
        implementation=0,
        seed=42,
    )
    samples = noise[tcod.noise.grid(shape, scale, origin=(0, 0))]

    print(samples.shape)

    return (samples + 1) / 2


def generate_island(
    map_width: int,
    map_height: int,
    engine: Engine,
    maximum_monsters: int = 10,
    maximum_items: int = 5,
):
    height_map = generate_heightmap(
        width=map_width,
        height=map_height,
        scale=0.09,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
    )

    x_center = map_width // 2
    y_center = map_height // 2

    ratio = map_width / map_height

    """Generate a new island map."""
    player = engine.player
    island = GameMap(engine, map_width, map_height, entities=[player])
    for x in range(map_width):
        for y in range(map_height):
            len_from_center_x = abs(x_center - x) / x_center
            len_from_center_y = abs(y_center - y) / y_center

            h = height_map[y][x] * (1 - max(len_from_center_x, len_from_center_y))

            if x == 0 or y == 0 or x == map_width - 1 or y == map_height - 1:
                island.tiles[x, y] = tile_types.water
            elif h < 0.15:
                island.tiles[x, y] = tile_types.water
            elif h < 0.2:
                island.tiles[x, y] = tile_types.sand
            elif h > 0.7:
                island.tiles[x, y] = tile_types.mountain
            elif h > 0.4 and h < 0.7:
                island.tiles[x, y] = tile_types.forrest
            else:
                island.tiles[x, y] = tile_types.grass

    player.place(map_width // 2, map_height // 2)

    number_of_monsters = random.randint(0, maximum_monsters)
    number_of_items = random.randint(0, maximum_items)

    while number_of_monsters > 0:
        x = random.randint(0, map_width - 1)
        y = random.randint(0, map_height - 1)

        if not any(entity.x == x and entity.y == y for entity in island.entities) and island.tiles[x, y][0]:
            if random.random() < 0.8:
                entity_factories.spawn_orc(island, x, y)
            else:
                entity_factories.spawn_troll(island, x, y)
            number_of_monsters -= 1

    while number_of_items > 0:
        x = random.randint(0, map_width - 1)
        y = random.randint(0, map_height - 1)

        if not any(entity.x == x and entity.y == y for entity in island.entities) and island.tiles[x, y][0]:
            if random.random() < 0.7:
                entity_factories.spawn_health_potion(island, x, y)
            elif random.random() < 0.8:
                entity_factories.spawn_fireball_scroll(island, x, y)
            elif random.random() < 0.9:
                entity_factories.spawn_confusion_scroll(island, x, y)
            else:
                entity_factories.spawn_lightning_scroll(island, x, y)
            number_of_items -= 1

    return island
