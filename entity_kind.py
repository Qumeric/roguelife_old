from enum import Enum, auto


class EntityKind(Enum):
    PLAYER = auto()

    ORC = auto()
    TROLL = auto()
    HUMAN = auto()
    WOLF = auto()

    ITEM = auto()

    UNKNOWN = auto()
