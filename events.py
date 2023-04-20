from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from blinker import Signal

if TYPE_CHECKING:
    from entity import Actor, Building, Entity


@dataclass
class TickEvent:
    time: datetime


@dataclass
class BaseMapEvent:
    x: int
    y: int


@dataclass
class ActorEvent(BaseMapEvent):
    actor: Actor


@dataclass
class SpawnEvent(BaseMapEvent):
    entity: Entity


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


@dataclass
class BuildingInteractEvent(ActorEvent):
    building: Building


spawn_signal = Signal("spawn")
attack_signal = Signal("attack")
pickup_signal = Signal("pickup")
drop_signal = Signal("drop")
use_signal = Signal("use")
move_signal = Signal("move")
building_interact_signal = Signal("building_interact")
