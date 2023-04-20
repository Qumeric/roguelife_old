from __future__ import annotations

from typing import TYPE_CHECKING, List

from components.base_component import ActorComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(ActorComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.game_map)

        self.engine.add_observation(f"I dropped the {item.name}.")
