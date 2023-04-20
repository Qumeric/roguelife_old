from typing import Union
import random

from entity_kind import EntityKind

# Define templates for each entity type
orc_templates = ["Gor{con}", "Ug{con}{vow}k", "Gri{con}{vow}kh", "Lur{con}{vow}"]
troll_templates = ["Ber{con}", "To{vow}{con}", "Wil{con}{vow}m", "Gna{vow}l", "Sku{vow}crusher"]
human_templates = ["Ar{vow}{con}orn", "Bor{vow}{con}ir", "Fara{vow}ir", "Eo{con}{vow}yn", "Eo{vow}{con}er"]
wolf_templates = ["Fen{con}{vow}r", "Hat{vow}", "Sk{con}{vow}ll", "Ger{vow}", "Fr{vow}{con}i"]

# Define consonants and vowels
consonants = "bcdfghjklmnpqrstvwxyz"
vowels = "aeiou"


# Function to generate names based on templates
def generate_name(kind: Union["EntityKind", str]) -> str:
    if isinstance(kind, str):
        kind_str = kind
    elif isinstance(kind, EntityKind):
        kind_str = kind.name
    else:
        raise RuntimeError(f"Invalid type of kind: {type(kind)}")
    match kind_str:
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


if __name__ == "__main__":
    orc_name = generate_name("ORC")
    troll_name = generate_name("TROLL")
    human_name = generate_name("HUMAN")
    wolf_name = generate_name("WOLF")

    print("Orc name:", orc_name)
    print("Troll name:", troll_name)
    print("Human name:", human_name)
    print("Wolf name:", wolf_name)
