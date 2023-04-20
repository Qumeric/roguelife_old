from __future__ import annotations

from typing import TYPE_CHECKING

from events import (
    AttackEvent,
    BuildingInteractEvent,
    DropEvent,
    MoveEvent,
    attack_signal,
    building_interact_signal,
    drop_signal,
    move_signal,
)
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Building, Entity, Item

from abc import ABC, abstractmethod


class Action(ABC):
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.game_map.engine

    @abstractmethod
    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.add_observation(f"I picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(self, entity: Actor, item: Item, target_xy: tuple[int, int] | None = None):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Actor | None:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)
        drop_signal.send(DropEvent(self.entity.x, self.entity.y, self.entity, self.item))


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Actor | None:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    @property
    def target_building(self) -> Building | None:
        """Return the building at this actions destination."""
        return self.engine.game_map.get_building_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class BuildingInteractAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_building
        if not target:
            raise exceptions.Impossible("No building to interact with.")

        building_interact_signal.send(
            self,
            event=BuildingInteractEvent(
                self.entity.x,
                self.entity.y,
                self.entity,
                target,
            ),
        )
        target.interactable.interact(self)


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense

        attack_signal.send(
            self,
            event=AttackEvent(
                self.entity.x,
                self.entity.y,
                self.entity,
                target,
            ),
        )

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.add_observation(f"{attack_desc} for {damage} hit points.", attack_color)
            target.fighter.take_damage(damage)
        else:
            self.engine.add_observation(f"{attack_desc} but does no damage.", attack_color)


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")

        move_signal.send(
            self,
            event=MoveEvent(
                self.entity.x,
                self.entity.y,
                self.entity,
                self.dx,
                self.dy,
            ),
        )
        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            MeleeAction(self.entity, self.dx, self.dy).perform()
        elif self.target_building:
            BuildingInteractAction(self.entity, self.dx, self.dy).perform()
        else:
            MovementAction(self.entity, self.dx, self.dy).perform()
