from datetime import timedelta
from random import randint

from components import consumable
from components.ai import AllyHuman, HostileEnemy
from components.fighter import Fighter
from components.interactable import TreeInteractable
from components.inventory import Inventory
from components.needs import Needs
from components.observation_log import ObservationLog
from components.relationships import Relationships
from components.stats import Stats
from entity import Actor, Building, IntelligentActor, Item
from entity_kind import EntityKind
from events import attack_signal, drop_signal, move_signal, pickup_signal, spawn_signal
from game_map import GameMap

visible_signals = [spawn_signal, attack_signal, pickup_signal, move_signal, drop_signal]


def create_player(x: int = 0, y: int = 0) -> IntelligentActor:
    """A special case.
    Don't forget to spawn later!
    """
    return IntelligentActor(
        x=x,
        y=y,
        char="@",
        color=(255, 255, 255),
        kind=EntityKind.PLAYER,
        name="Player",
        ai_cls=AllyHuman,
        fighter=Fighter(hp=30, defense=2, power=5),
        inventory=Inventory(capacity=26),
        needs=Needs(max_hunger=100, max_thirst=100, max_sleepiness=1000, max_lonliness=1000),
        stats=Stats(age=timedelta(days=20 * 365), intelligence=10, strength=10, dexterity=10, stamina=10),
        observation_log=ObservationLog(capacity=1024),
        relationships=Relationships(),
        signals_to_listen=visible_signals,
    )


def spawn_human(game_map: GameMap, x: int, y: int) -> IntelligentActor:
    human = IntelligentActor(
        x=x,
        y=y,
        char="h",
        color=(127, 127, 127),
        kind=EntityKind.HUMAN,
        ai_cls=AllyHuman,
        fighter=Fighter(hp=10, defense=0, power=3),
        inventory=Inventory(capacity=0),
        needs=Needs(
            max_hunger=randint(80, 120),
            max_thirst=randint(80, 120),
            max_sleepiness=randint(800, 1200),
            max_lonliness=1000,
        ),
        stats=Stats(
            age=timedelta(days=randint(15, 60) * 365),
            intelligence=randint(1, 13),
            strength=randint(3, 15),
            dexterity=randint(3, 15),
            stamina=randint(3, 15),
        ),
        observation_log=ObservationLog(capacity=512),
        relationships=Relationships(),
        signals_to_listen=visible_signals,
    )
    game_map.spawn(human)
    return human


### Actors ###


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
        needs=Needs(
            max_hunger=randint(70, 100),
            max_thirst=randint(100, 200),
            max_sleepiness=randint(1500, 2000),
            max_lonliness=800,
        ),
        stats=Stats(
            age=timedelta(days=randint(14, 40) * 365),
            intelligence=randint(1, 8),
            strength=randint(5, 17),
            dexterity=randint(3, 12),
            stamina=randint(5, 17),
        ),
        observation_log=ObservationLog(capacity=512),
        relationships=Relationships(),
        signals_to_listen=visible_signals,
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
        needs=Needs(
            max_hunger=randint(50, 80),
            max_thirst=randint(300, 800),
            max_sleepiness=randint(3500, 5000),
            max_lonliness=3000,
        ),
        stats=Stats(
            age=timedelta(days=randint(14, 40) * 365),
            intelligence=randint(1, 8),
            strength=randint(10, 25),
            dexterity=randint(1, 5),
            stamina=randint(10, 30),
        ),
        observation_log=ObservationLog(capacity=256),
        relationships=Relationships(),
        signals_to_listen=visible_signals,
    )
    game_map.spawn(troll)
    return troll


### Items ###


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


def spawn_apple(game_map: GameMap, x: int, y: int):
    apple = Item(
        x=x, y=y, char="a", color=(255, 0, 0), name="Apple", consumable=consumable.Food(nutrition=10, water_content=8)
    )
    game_map.spawn(entity=apple)
    return apple


### Buildings ###
def spawn_tree(game_map: GameMap, x: int, y: int):
    tree = Building(
        x=x,
        y=y,
        char="T",
        color=(255, 255, 255),
        name="Tree",
        interactable=TreeInteractable(),
    )

    game_map.spawn(entity=tree)
    return tree
