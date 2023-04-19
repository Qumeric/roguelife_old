from __future__ import annotations

from typing import List, TYPE_CHECKING
from dataclasses import dataclass

from components.base_component import BaseComponent

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

        print(f"Add observation to {self.parent.name}: {event}")

    def __str__(self) -> str:
        """Represent the log as text suitable for LLMs.

        It is supposed to be overloaded by agents.
        """
        return str(self.observations)
