from __future__ import annotations

from dataclasses import dataclass
from random import randint
from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from events import BuildingInteractEvent, building_interact_signal
import actions
import entity_factories

if TYPE_CHECKING:
    from entity import Building


class Interactable(BaseComponent):
    parent: Building

    def interact(self, action: actions.BuildingInteractAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()


@dataclass
class TreeInteractable(Interactable):
    max_energy: int = 100
    current_energy: int = 10
    energy_for_apple: int = 10

    @property
    def apples_on_tree(self) -> int:
        return self.current_energy // self.energy_for_apple

    def interact(self, action: actions.BuildingInteractAction) -> None:
        engine = action.engine
        tree = self.parent
        actor = action.entity
        game_map = engine.game_map

        building_interact_signal.send(
            self,
            event=BuildingInteractEvent(
                tree.x,
                tree.y,
                actor,
                tree,
            ),
        )

        if self.apples_on_tree == 0:
            return

        apples_to_drop = randint(1, self.apples_on_tree)
        self.current_energy -= apples_to_drop * self.energy_for_apple
        attempts = apples_to_drop * 2

        while apples_to_drop > 0 and attempts > 0:
            dx = randint(1, 3)
            dy = randint(1, 3)
            sx = randint(0, 1) * 2 - 1
            sy = randint(0, 1) * 2 - 1
            x = tree.x + dx * sx
            y = tree.y + dy * sy

            if game_map.can_spawn_at(x, y):
                entity_factories.spawn_apple(
                    game_map,
                    x,
                    y,
                )
                apples_to_drop -= 1
            attempts -= 1
