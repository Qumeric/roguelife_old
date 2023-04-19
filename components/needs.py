from __future__ import annotations

from typing import List, TYPE_CHECKING

from dataclasses import dataclass
from components.base_component import ActorComponent

if TYPE_CHECKING:
    from entity import Actor, Item


@dataclass
class Needs(ActorComponent):
    # Basic
    max_hunger: int
    max_thirst: int
    max_sleepiness: int

    # Other
    max_lonliness: int

    hunger = 0
    thirst = 0
    sleepiness = 0
    lonliness = 0

    # TODO will be set later but is it ok to have dataclass?
    parent: Actor = None
    # TODO how often does reflection happen?
    reflection = 10

    def report(self):
        return f"Hunger: {self.hunger}/{self.max_hunger},\
Thirst: {self.thirst}/{self.max_thirst},\
Sleepiness: {self.sleepiness}/{self.max_sleepiness},\
Lonliness: {self.lonliness}/{self.max_lonliness}"

    # TODO it shall be possible to have different change rates for different creatures
    def update(self):
        self.hunger += 1
        self.thirst += 1
        self.sleepiness += 1
        self.lonliness += 1

        if self.hunger >= self.max_hunger:
            self.parent.observation_log.add_observation(text="I am starving!", event=None)
            self.parent.fighter.take_damage(1)
            self.hunger = self.max_hunger

        if self.thirst >= self.max_thirst:
            self.parent.observation_log.add_observation(text="I am dying of thirst!", event=None)
            self.parent.fighter.take_damage(1)
            self.thirst = self.max_thirst

        if self.sleepiness >= self.max_sleepiness:
            self.parent.observation_log.add_observation(text="I am extremely tired!", event=None)
            self.parent.fighter.take_damage(1)
            self.thirst = self.max_sleepiness

        if self.lonliness >= self.max_lonliness:
            self.parent.observation_log.add_observation(text="I am extremely lonely!", event=None)
            self.lonliness = self.max_lonliness
