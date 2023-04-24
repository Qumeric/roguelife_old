from __future__ import annotations

from typing import TYPE_CHECKING

import color
import constants

if TYPE_CHECKING:
    from tcod import Console

    from engine import Engine


def render_bar(console: Console, current_value: int, maximum_value: int, total_width: int) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=constants.map_height + 2, width=20, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(x=0, y=constants.map_height + 2, width=bar_width, height=1, ch=1, bg=color.bar_filled)

    console.print(x=1, y=constants.map_height + 2, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text)


def render_names_at_mouse_location(console: Console, x: int, y: int, engine: Engine) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = engine.game_map.get_names_at_location(x=mouse_x, y=mouse_y)

    console.print(x=x, y=y, string=names_at_mouse_location)
