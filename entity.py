from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar
import math

from tcod.map import compute_fov
import numpy as np

from entity_kind import EntityKind
from events import AttackEvent, BaseMapEvent, MoveEvent, TickEvent
from exceptions import Impossible
from game_time import tick_signal
from name_generator import generate_name
from render_order import RenderOrder
import constants

if TYPE_CHECKING:
    from blinker import Signal

    from components.ai import BaseAI, IntelligentCreature
    from components.consumable import Consumable
    from components.fighter import Fighter
    from components.interactable import Interactable
    from components.inventory import Inventory
    from components.needs import Needs
    from components.observation_log import ObservationLog
    from components.stats import Stats
    from game_map import GameMap


T = TypeVar("T", bound="Entity")


class Entity(ABC):
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: GameMap | Inventory

    def __init__(
        self,
        name: str,
        parent: GameMap | None = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        kind: EntityKind = EntityKind.UNKNOWN,
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

        tick_signal.connect(receiver=self.tick)

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    @property
    def full_name(self) -> str:
        return f"{self.name} ({self.kind.name})"

    @abstractmethod
    def tick(self, _sender: Any, event: TickEvent) -> None:
        """Called every tick. It should update all components."""

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
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

    def __str__(self):
        return f"{self.name} ({self.kind.name})"


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        kind: EntityKind = EntityKind.UNKNOWN,
        name: str | None = None,
        ai_cls: type[BaseAI],
        fighter: Fighter,
        inventory: Inventory,
        needs: Needs,
        stats: Stats,
        observation_log: ObservationLog,
        signals_to_listen: list[Signal],
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
            name=name or generate_name(kind),
        )

        self.ai: BaseAI | None = ai_cls(self)

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.needs = needs
        self.needs.parent = self

        self.stats = stats
        self.stats.parent = self

        self.observation_log = observation_log
        self.observation_log.parent = self

        self.visible = np.full(
            (constants.map_width, constants.map_height), fill_value=False, order="F"
        )  # Tiles the actor can currently see.
        self.explored = np.full(
            (constants.map_width, constants.map_height), fill_value=False, order="F"
        )  # Tiles the actor has seen before.

        self.eyesight = eyesight

        for signal in signals_to_listen:
            signal.connect(self.handle_event)

    def _update_fov(self) -> None:
        self.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.x, self.y),
            radius=self.eyesight,
        )

        self.explored |= self.visible

    def tick(self, _sender: Any, event: TickEvent) -> None:
        # Make ai take its turn.
        # TODO a hack but ok for now
        if self.char != "@" and self.ai:
            try:
                self.ai.perform()
            except Impossible:
                pass  # Ignore impossible action exceptions from AI.

        self._update_fov()

        self.needs.update()

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    def can_see(self, target_x: int, target_y: int) -> bool:
        return self.is_alive and self.visible[target_x, target_y]

    def handle_event(self, _sender: Any, event: BaseMapEvent):
        if not self.can_see(event.x, event.y):
            return
        # print(f"{self.name} observes {event}")
        match event:
            case AttackEvent(_, _, actor, target):
                if actor == self:
                    self.observation_log.add_observation(f"I attacked {target.full_name}", event=event)
                if target == self:
                    self.observation_log.add_observation(f"I was attacked by {actor.full_name}", event=event)
            case MoveEvent(_, _, actor, dx, dy):
                print(f"{actor.name} moved by ({dx}, {dy})")
            case _:
                print("Unknown event type")


class IntelligentActor(Actor):
    """A specific actor which has intelligent ai."""

    ai: IntelligentCreature


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str,
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

    def tick(self, _sender: Any, event: TickEvent) -> None:
        pass


class Building(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str,
        interactable: Interactable,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            kind=EntityKind.BUILDING,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.BUILDING,
        )

        self.interactable = interactable
        self.interactable.parent = self

    def tick(self, _sender: Any, event: TickEvent) -> None:
        self.interactable.update()
