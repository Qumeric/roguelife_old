from __future__ import annotations
import numpy as np

from enum import Enum, auto
import copy
import math
import tcod
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union
import constants

from render_order import RenderOrder
from events import BaseEvent, AttackEvent, MoveEvent, PickupEvent, UseEvent

from name_generator import generate_name

from entity_kind import EntityKind

if TYPE_CHECKING:
    from blinker import Signal
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.observation_log import ObservationLog
    from game_map import GameMap


T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        kind: EntityKind = EntityKind.UNKNOWN,
        name: Optional[str] = None,
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.kind = kind
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    @property
    def full_name(self) -> str:
        return f"{self.name} ({self.kind.name})"

    def place(self, x: int, y: int, game_map: Optional[GameMap] = None) -> None:
        """Place this entitiy at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if game_map:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.game_map:
                    self.game_map.entities.remove(self)
            self.parent = game_map
            game_map.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        kind: EntityKind = EntityKind.UNKNOWN,
        name: Optional[str] = None,
        ai_cls: Type[BaseAI],
        fighter: Fighter,
        inventory: Inventory,
        observation_log: ObservationLog,
        signals_to_listen: List[Signal],
        eyesight: int = 8,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            kind=kind,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.name = name or generate_name(kind)

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.observation_log = observation_log
        self.observation_log.parent = self

        self.visible = np.full(
            (constants.map_width, constants.map_height), fill_value=False, order="F"
        )  # Tiles the actor can currently see. Updated each turn by the engine.
        self.explored = np.full(
            (constants.map_width, constants.map_height), fill_value=False, order="F"
        )  # Tiles the actor has seen before. Updated each turn by the engine.

        self.eyesight = eyesight

        for signal in signals_to_listen:
            signal.connect(self.handle_event)

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    def can_see(self, target_x: int, target_y: int) -> bool:
        return self.is_alive and self.visible[target_x, target_y]

    def handle_event(self, sender, event: BaseEvent):
        if not self.can_see(event.x, event.y):
            return
        print(f"{self.name} observes {event}")
        match event:
            case AttackEvent(_, _, _, _, attacker, target):
                if attacker == self:
                    self.observation_log.add_observation(f"I attacked {target.full_name}", event)
                if target == self:
                    self.observation_log.add_observation(f"I was attacked by {attacker.full_name}", event)
            case MoveEvent(_, _, _, _, entity, dx, dy):
                print(f"{entity} moved by ({dx}, {dy})")
            case _:
                print("Unknown event type")


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: Optional[str] = None,
        consumable: Consumable,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            kind=EntityKind.ITEM,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable
        self.consumable.parent = self
