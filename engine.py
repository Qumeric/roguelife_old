from __future__ import annotations

from typing import TYPE_CHECKING
import lzma
import pickle

from tcod.console import Console

from render_functions import render_bar, render_names_at_mouse_location
import color
import constants

if TYPE_CHECKING:
    from entity import IntelligentActor
    from events import BaseMapEvent
    from game_map import GameMap


class Engine:
    game_map: GameMap
    mouse_location: tuple[int, int]

    def __init__(self, player: IntelligentActor):
        self.mouse_location = (0, 0)
        self.player = player

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.player.observation_log.render(console=console, x=21, y=constants.map_height + 2, width=40, height=5)

        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_names_at_mouse_location(console=console, x=21, y=constants.map_height + 1, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    def add_observation(
        self, observation: str, fg: tuple[int, int, int] = color.white, event: BaseMapEvent | None = None
    ):
        self.player.observation_log.add(observation, fg, event)
