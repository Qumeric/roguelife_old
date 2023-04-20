from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, List

from components.base_component import ActorComponent

if TYPE_CHECKING:
    from entity import Actor, Item


@dataclass
class Stats(ActorComponent):
    age: timedelta

    # Basic
    intelligence: int
    strength: int
    dexterity: int
    stamina: int

    # TODO will be set later but is it ok to have dataclass?
    parent: Actor = None
    # TODO how often does reflection happen?
    reflection = 10

    def report(self):
        return f"Intelligence: {self.intelligence},\
Strength: {self.strength},\
Stamina: {self.stamina},\
Dexterity: {self.dexterity},\
Age: {self.age.days // 365}"

    def update(self):
        self.age += timedelta(minutes=1)
