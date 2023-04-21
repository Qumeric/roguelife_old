from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import ActorComponent

if TYPE_CHECKING:
    from entity import Actor


class Relationships(ActorComponent):
    state: dict[str, int]

    def __init__(self) -> None:
        self.state = {}
        super().__init__()

    def meet(self, actor: Actor) -> bool:
        """
        Adds a new relationship if it doesn't exist yet.

        Returns True if a new relationship was added.
        """
        if actor.name not in self.state:
            self.state[actor.name] = 0
            return True
        return False

    def update(self):
        return super().update()

    def report(self):
        return f"Relationships: {self.state}"
