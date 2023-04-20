from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import ActorComponent
from render_order import RenderOrder
import color

if TYPE_CHECKING:
    from entity import Actor


class Fighter(ActorComponent):
    parent: Actor

    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property
    def hp(self) -> int:
        return self._hp

    def _set_hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE
        self.observations.add_observation(
            "I am dead!",
            color.death,
        )

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self._set_hp(new_hp_value)

        self.observations.add_observation(
            text=f"I healed! My HP increased by {amount_recovered} to {self.hp}", event=None
        )
        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self._set_hp(self.hp - amount)

        self.observations.add_observation(text=f"I took damage! My HP decreased by {amount} to {self.hp}", event=None)
