from enum import Enum, auto


class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    BUILDING = auto()
    ACTOR = auto()
