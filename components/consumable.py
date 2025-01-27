from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import ActionOrHandler, AreaRangedAttackHandler, SingleRangedAttackHandler
import actions
import color
import components.ai
import components.inventory

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def update(self) -> None:
        pass

    def get_action(self, consumer: Actor) -> ActionOrHandler | None:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    @abstractmethod
    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        item = self.parent
        inventory = item.parent

        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(item)
            inventory.parent.observation_log.add(f"I consumed the {self.parent.name}")


class Food(Consumable):
    def __init__(self, nutrition: int, water_content: int):
        self.nutrition = nutrition
        self.water_content = water_content

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        self.consume()
        consumer.needs.eat(self)


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        # TODO change to event
        self.engine.add_observation(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target,
            previous_ai=target.ai,
            turns_remaining=self.number_of_turns,
        )
        self.consume()


class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                # TODO change to event
                self.engine.add_observation(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        self.consume()
        consumer.fighter.heal(self.amount)


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.game_map.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            # TODO change to event
            self.engine.add_observation(
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")
