from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from components.observation_log import ObservationLog
from entity import Actor, Item
from game_map import GameMap

from events import attack_signal

from typing import TYPE_CHECKING
from entity_kind import EntityKind


def create_player(x: int = 0, y: int = 0):
    """A special case.
    Don't forget to spawn later!
    """
    return Actor(
        x=x,
        y=y,
        char="@",
        color=(255, 255, 255),
        kind=EntityKind.PLAYER,
        name="Player",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=30, defense=2, power=5),
        inventory=Inventory(capacity=26),
        observation_log=ObservationLog(capacity=1024),
        signals_to_listen=[attack_signal],
    )


def spawn_orc(game_map: GameMap, x: int, y: int):
    orc = Actor(
        x=x,
        y=y,
        char="o",
        color=(63, 127, 63),
        kind=EntityKind.ORC,
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=10, defense=0, power=3),
        inventory=Inventory(capacity=0),
        observation_log=ObservationLog(capacity=512),
        signals_to_listen=[attack_signal],
    )
    game_map.spawn(orc)
    return orc


def spawn_troll(game_map: GameMap, x: int, y: int):
    troll = Actor(
        x=x,
        y=y,
        char="T",
        color=(0, 127, 0),
        kind=EntityKind.TROLL,
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=16, defense=1, power=4),
        inventory=Inventory(capacity=0),
        observation_log=ObservationLog(capacity=512),
        signals_to_listen=[attack_signal],
    )
    game_map.spawn(troll)
    return troll


def spawn_confusion_scroll(game_map: GameMap, x: int, y: int):
    confusion_scroll = Item(
        x=x,
        y=y,
        char="~",
        color=(207, 63, 255),
        name="Confusion Scroll",
        consumable=consumable.ConfusionConsumable(number_of_turns=10),
    )
    game_map.spawn(entity=confusion_scroll)
    return confusion_scroll


def spawn_fireball_scroll(game_map: GameMap, x: int, y: int):
    fireball_scroll = Item(
        x=x,
        y=y,
        char="~",
        color=(255, 0, 0),
        name="Fireball Scroll",
        consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
    )
    game_map.spawn(entity=fireball_scroll)
    return fireball_scroll


def spawn_health_potion(game_map: GameMap, x: int, y: int):
    health_potion = Item(
        x=x,
        y=y,
        char="!",
        color=(127, 0, 255),
        name="Health Potion",
        consumable=consumable.HealingConsumable(amount=4),
    )
    game_map.spawn(entity=health_potion)
    return health_potion


def spawn_lightning_scroll(game_map: GameMap, x: int, y: int):
    lightning_scroll = Item(
        x=x,
        y=y,
        char="~",
        color=(255, 255, 0),
        name="Lightning Scroll",
        consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
    )
    game_map.spawn(entity=lightning_scroll)
    return lightning_scroll
