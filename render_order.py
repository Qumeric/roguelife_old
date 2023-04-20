from enum import auto, Enum


class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    BUILDING = auto()
    ACTOR = auto()
