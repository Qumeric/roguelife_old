from __future__ import annotations

from collections.abc import Iterable, Reversible
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import textwrap

from components.base_component import BaseComponent
from game_time import current_datetime
import color

if TYPE_CHECKING:
    from datetime import datetime

    import tcod.console

    from entity import Actor
    from events import BaseEvent


@dataclass
class Observation:
    """An observation made by an actor."""

    text: str
    event: BaseEvent | None
    fg: tuple[int, int, int] = color.white
    gametime: datetime = field(default_factory=current_datetime)

    def __str__(self) -> str:
        formatted_datime = self.gametime.strftime("%y-%m-%d %H:%M")
        return f"[{formatted_datime}]: {self.text}"


class ObservationLog(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.observations: list[Observation] = []

    def add(self, text: str, fg: tuple[int, int, int] = color.white, event: BaseEvent | None = None) -> None:
        """Add a observation to this log.

        `text` is the message text, `fg` is the text color.
        """
        self.observations.append(Observation(text, event, fg))

        if len(self.observations) > self.capacity:
            self.observations.pop(0)

        print(f"Add observation to {self.parent.name}: {text}")

    def update(self) -> None:
        return super().update()

    def __str__(self) -> str:
        """Represent the log as text suitable for LLMs.

        It is supposed to be overloaded by agents.
        """
        return str(self.observations)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text message."""
        for line in string.splitlines():  # Handle newlines in messages.
            yield from textwrap.wrap(
                line,
                width,
                expand_tabs=True,
            )

    @classmethod
    def render_observations(
        cls,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        observations: Reversible[Observation],
    ) -> None:
        """Render the observations provided.

        The `messages` are rendered starting at the last message and working
        backwards.
        """
        y_offset = height - 1

        for observation in reversed(observations):
            for line in reversed(list(cls.wrap(str(observation), width))):
                console.print(x=x, y=y + y_offset, string=line, fg=observation.fg)
                y_offset -= 1
                if y_offset < 0:
                    return  # No more space to print messages.

    def render(
        self,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Render this log over the given area.

        Shall be used only for the player's log.

        `x`, `y`, `width`, `height` is the rectangular region to render onto
        the `console`.
        """
        self.render_observations(console, x, y, width, height, self.observations)
