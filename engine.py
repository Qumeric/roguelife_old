from __future__ import annotations

from typing import TYPE_CHECKING
import lzma
import pickle

from tcod.console import Console
from tcod.map import compute_fov

from game_time import tick as global_tick
from render_functions import render_bar, render_names_at_mouse_location
import color
import constants
import exceptions

if TYPE_CHECKING:
    from entity import Actor
    from events import Event
    from game_map import GameMap

from random import random


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
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
        self, observation: str, fg: Tuple[int, int, int] = color.white, event: Optional[BaseEvent] = None
    ):
        self.player.observation_log.add_observation(observation, event)
