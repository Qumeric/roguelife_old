from __future__ import annotations

from blinker import Signal
from typing import TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from entity import Actor


@dataclass
class BaseEvent:
    # TODO introduce a class for in-game time
    x: int
    y: int
    timestamp: int
    message: str

    def __str__(self) -> str:
        return f"[{self.timestamp}]: {self.message} at ({self.x}, {self.y})"


@dataclass
class AttackEvent(BaseEvent):
    attacker: Actor
    target: Actor

@dataclass
class PickupEvent(BaseEvent):
    actor: Actor
    item: Actor

@dataclass
class DropEvent(BaseEvent):
    actor: Actor
    item: Actor

@dataclass
class UseEvent(BaseEvent):
    actor: Actor
    item: Actor

@dataclass
class MoveEvent(BaseEvent):
    actor: Actor
    direction: str

attack_signal = Signal("attack")
