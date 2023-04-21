from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import ActorComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(ActorComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.gold = 0
        self.items: list[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.game_map)

        self.engine.add_observation(f"I dropped the {item.name}.")

    def report(self) -> str:
        """
        Returns a report of the items in the inventory.
        """
        if not self.items:
            return "I have nothing."

        items = ", ".join([item.name for item in self.items])

        return f"I have {items}."
