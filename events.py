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

    def __str__(self) -> str:
        return f"[{self.timestamp}]: Event at ({self.x}, {self.y})"


@dataclass
class ActorEvent(BaseEvent):
    actor: Actor


@dataclass
class AttackEvent(ActorEvent):
    target: Actor


@dataclass
class PickupEvent(ActorEvent):
    item: Actor


@dataclass
class DropEvent(ActorEvent):
    item: Actor


@dataclass
class UseEvent(ActorEvent):
    item: Actor


@dataclass
class MoveEvent(ActorEvent):
    dx: int
    dy: int


attack_signal = Signal("attack")
pickup_signal = Signal("pickup")
drop_signal = Signal("drop")
use_signal = Signal("use")
move_signal = Signal("move")
