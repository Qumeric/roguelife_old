from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
import random

import numpy as np  # type: ignore
import tcod

from actions import (
    Action,
    BumpAction,
    LookAroundAction,
    MeleeAction,
    MovementAction,
    ObserveIdentityAction,
    ObserveInventoryAction,
    ObserveNeedsAction,
    ObserveStatsAction,
    WaitAction,
)
from llm import generate_reflection
import tile_types

if TYPE_CHECKING:
    from entity import Actor, IntelligentActor


# TODO maybe it shall be moved from components? It is kinda weird...
class BaseAI(Action):
    @abstractmethod
    def perform(self) -> None:
        pass

    def get_path_to(self, dest_x: int, dest_y: int) -> list[tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: list[list[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class IntelligentCreature(BaseAI):
    entity: IntelligentActor

    def look_around(self) -> None:
        game_map = self.entity.game_map
        fov = self.entity.visible

        my_tile = game_map.tiles[self.entity.x, self.entity.y]
        my_tile_name = tile_types.get_name(my_tile)

        vision_log = [f"I am staying on {my_tile_name} at [{self.entity.x}, {self.entity.y}]. I see the following:"]

        for x in range(game_map.width):
            for y in range(game_map.height):
                if not fov[x, y]:
                    continue
                for e in game_map.get_entities_at_location(x, y):
                    if e == self.entity:
                        continue
                    vision_log.append(f"  - {e} at [{x}, {y}]")

                actor = game_map.get_actor_at_location(x, y)
                if actor and actor != self.entity:
                    is_new_relationship = self.entity.relationships.meet(actor)
                    if is_new_relationship:
                        self.entity.observation_log.add(f"I met {actor} at [{x}, {y}]")

        vision_text = "\n".join(vision_log)
        self.entity.observation_log.add(vision_text)
        return

    def observe_needs(self) -> None:
        needs_report = self.entity.needs.report()
        self.entity.observation_log.add(
            text=f"I am thinking about how I feel and observe the following: {needs_report}"
        )

    def observe_inventory(self) -> None:
        inventory_report = self.entity.inventory.report()
        self.entity.observation_log.add(
            text=f"I am thinking about what I have and observe the following: {inventory_report}"
        )

    def observe_stats(self) -> None:
        stats_report = self.entity.stats.report()
        self.entity.observation_log.add(text=f"I am thinking about who I am and observe the following: {stats_report}")

    def observe_relationships(self) -> None:
        relationships_report = self.entity.relationships.report()
        self.entity.observation_log.add(text=f"My relationships are: {relationships_report}")

    def observe_identity(self) -> None:
        identity_report = self.entity.identity.report()
        self.entity.observation_log.add(text=f"My origin is: {identity_report}")

    def reflect(self) -> None:
        """Reflection as in 'Generative Agents' paper"""
        reflection = generate_reflection(self.entity.name, self.entity.observation_log)
        self.entity.observation_log.add(reflection)


class Player(IntelligentCreature):
    def __init__(self, entity: IntelligentActor):
        super().__init__(entity)
        self.path: list[tuple[int, int]] = []

    def perform(self):
        pass


class AllyHuman(IntelligentCreature):
    def __init__(self, entity: IntelligentActor):
        super().__init__(entity)
        self.path: list[tuple[int, int]] = []

    def perform(self) -> None:
        dest_x = random.randint(-1, 2)
        dest_y = random.randint(-1, 2)

        if random.random() < 0.01:
            return ObserveStatsAction(self.entity).perform()
        if random.random() < 0.02:
            return ObserveNeedsAction(self.entity).perform()
        if random.random() < 0.03:
            return ObserveInventoryAction(self.entity).perform()
        if random.random() < 0.05:
            return ObserveIdentityAction(self.entity).perform()
        if random.random() < 0.1:
            return LookAroundAction(self.entity).perform()
        if random.random() < 0.2:
            return WaitAction(self.entity).perform()
        return MovementAction(self.entity, dest_x, dest_y).perform()


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: list[tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity,
                dest_x - self.entity.x,
                dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(self, entity: Actor, previous_ai: BaseAI | None, turns_remaining: int):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            # TODO change to event
            self.engine.add_observation(f"The {self.entity.name} is no longer confused.")
            self.entity.ai = self.previous_ai
            return
        # Pick a random direction
        direction_x, direction_y = random.choice(
            [
                (-1, -1),  # Northwest
                (0, -1),  # North
                (1, -1),  # Northeast
                (-1, 0),  # West
                (1, 0),  # East
                (-1, 1),  # Southwest
                (0, 1),  # South
                (1, 1),  # Southeast
            ]
        )

        self.turns_remaining -= 1

        # The actor will either try to move or attack in the chosen random direction.
        # Its possible the actor will just bump into the wall, wasting a turn.
        BumpAction(
            self.entity,
            direction_x,
            direction_y,
        ).perform()
