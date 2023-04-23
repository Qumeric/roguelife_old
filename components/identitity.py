from __future__ import annotations

from enum import Enum, auto
import random

from components.base_component import ActorComponent
from entity_kind import EntityKind
from llm import generate_identitiy

# Define templates for each entity type
orc_templates = ["Gor{con}", "Ug{con}{vow}k", "Gri{con}{vow}kh", "Lur{con}{vow}"]
troll_templates = ["Ber{con}", "To{vow}{con}", "Wil{con}{vow}m", "Gna{vow}l", "Sku{vow}crusher"]
human_templates = ["Ar{vow}{con}orn", "Bor{vow}{con}ir", "Fara{vow}ir", "Eo{con}{vow}yn", "Eo{vow}{con}er"]
wolf_templates = ["Fen{con}{vow}r", "Hat{vow}", "Sk{con}{vow}ll", "Ger{vow}", "Fr{vow}{con}i"]

# Define consonants and vowels
consonants = "bcdfghjklmnpqrstvwxyz"
vowels = "aeiou"


class Gender(Enum):
    MALE = auto()
    FEMALE = auto()
    UNKNOWN = auto()


# TODO EnitityKind should probably be here too
class Identity(ActorComponent):
    def __init__(self, kind: EntityKind, name: str | None) -> None:
        super().__init__()
        self.name = name or self.generate_name(kind)
        if kind == EntityKind.HUMAN or kind == EntityKind.PLAYER:
            self.text = generate_identitiy("male", self.name)
        else:
            self.text = f"I am a {kind.name.lower()}."

        is_male = "[male]" in self.text
        is_female = "[female]" in self.text

        if not is_male and not is_female:
            self.gender = Gender.UNKNOWN
        if is_male and is_female:
            raise ValueError("Generated descriptions confuses male and female")
        if is_male:
            self.gender = Gender.MALE
        if is_female:
            self.gender = Gender.FEMALE

    def generate_name(self, kind: EntityKind) -> str:
        match kind.name:
            case "ORC":
                template = random.choice(orc_templates)
            case "TROLL":
                template = random.choice(troll_templates)
            case "HUMAN":
                template = random.choice(human_templates)
            case "WOLF":
                template = random.choice(wolf_templates)
            case _:
                raise ValueError(f"Invalid entity kind {kind}")

        name = template.format(con=random.choice(consonants), vow=random.choice(vowels))
        return name.capitalize()

    def update(self):
        return super().update()

    def report(self):
        return self.text
