from __future__ import annotations

from typing import List, TYPE_CHECKING
from dataclasses import dataclass

from components.base_component import BaseComponent
from message_log import MessageLog

if TYPE_CHECKING:
    from entity import Actor, Item
    from events import BaseEvent


@dataclass
class Observation:
    """An observation made by an actor."""

    text: str
    event: BaseEvent

    def __str__(self) -> str:
        return self.text


class ObservationLog(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.observations: List[Event] = []

    def add_observation(self, text: str, event: BaseEvent) -> None:
        """Add a observation to this log.

        `text` is the message text, `fg` is the text color.
        """
        self.observations.append(Observation(text, event))

        if len(self.observations) > self.capacity:
            self.observations.pop(0)

        print(f"Add observation to {self.parent.name}: {text}")

    def __str__(self) -> str:
        """Represent the log as text suitable for LLMs.

        It is supposed to be overloaded by agents.
        """
        return str(self.observations)

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
            for line in reversed(list(MessageLog.wrap(observation.text, width))):
                # TODO add coloring similar to message_log
                console.print(x=x, y=y + y_offset, string=line)
                y_offset -= 1
                if y_offset < 0:
                    return  # No more space to print messages.
