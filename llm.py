# ruff: noqa: E501
from typing import TYPE_CHECKING
import os

from dotenv import load_dotenv
import jinja2
import openai

from components.observation_log import ObservationLog
from constants import cost_saving_mode

if TYPE_CHECKING:
    from typing import Any

load_dotenv()
openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_SK")

promptLoader = jinja2.FileSystemLoader(searchpath="./prompts/")
promptEnv = jinja2.Environment(loader=promptLoader)


def get_identity_prompt(gender: str, name: str) -> str:
    PROMPT_FILE = "identity.md.jinja"
    template = promptEnv.get_template(PROMPT_FILE)

    male_examples = [
        "Cedric Ironhammer is a skilled blacksmith who found himself on the island unexpectedly. He's determined to use his abilities to contribute to the survival and prosperity of the community. Cedric is known for his meticulous craftsmanship and never backs down from a challenge, even in this new and unfamiliar environment.",
        "Gareth Swiftfoot is an agile and cunning scout who uses his sharp senses to explore the island and gather valuable information. He's unattached and appreciates the freedom to roam and discover. Gareth is known for his quick thinking and ability to find hidden resources, making him a valuable asset to the community.",
        "Alistair Windwalker is a skillful hunter who woke up on the island without any recollection of his past life. He uses his keen instincts to provide food for the community and is always on the lookout for potential threats. Alistair is a solitary individual who finds solace in nature but is willing to work with others to ensure their collective survival.",
    ]

    female_examples = [
        "Iris Stormweaver is a fearless warrior who now finds herself stranded on the island. She is determined to protect her fellow islanders from any dangers they may face. Iris is a natural leader with an indomitable spirit, never shying away from a challenge or the opportunity to defend those in need.",
        "Maeve Brightsong is a gifted bard who seeks to bring joy and hope to the island's inhabitants with her enchanting music and stories. She is a beacon of light in these uncertain times, using her talents to lift the spirits of those around her. Maeve is a kind and empathetic soul, always willing to lend a listening ear or offer comforting words to those in need.",
        "Elowen Thistledown is an experienced herbalist who mysteriously found herself on the island. She is knowledgeable about the local flora and is dedicated to using her skills to heal and protect her fellow islanders. Elowen is a patient and compassionate person, tirelessly working to improve the health and well-being of the community.",
    ]

    templateVars: dict[str, Any] = {
        "gender": gender,
        "name": name,
    }

    if gender == "female":
        templateVars["examples"] = female_examples
    elif gender == "male":
        templateVars["examples"] = male_examples
    else:
        raise ValueError("Invalid gender")

    return template.render(templateVars)


def get_reflection_prompt(name: str, observationLog: ObservationLog):
    PROMPT_FILE = "reflection.md.jinja"
    template = promptEnv.get_template(PROMPT_FILE)

    templateVars: dict[str, Any] = {
        "observations": observationLog.observations,
    }

    return template.render(templateVars)


hardcoded_identities = [
    """
[male] is a skilled blacksmith who found himself on the island unexpectedly. He's determined to use his abilities to contribute to the survival and prosperity of the community. [male] is known for his meticulous craftsmanship and never backs down from a challenge, even in this new and unfamiliar environment.
""".strip(),
    """
[female] is a talented farmer who suddenly woke up on the island, leaving her old life behind. Despite her situation, she remains optimistic and has taken the initiative to cultivate crops and ensure a stable food supply. [female] is resourceful and adaptable, making the best of her circumstances to help those around her.
""".strip(),
    """
[male] is an agile and cunning scout who uses his sharp senses to explore the island and gather valuable information. He's unattached and appreciates the freedom to roam and discover. [male] is known for his quick thinking and ability to find hidden resources, making him a valuable asset to the community.
""".strip(),
    """
[female] is an experienced herbalist who mysteriously found herself on the island. [female] is knowledgeable about the local flora and is dedicated to using her skills to heal and protect her fellow islanders. [male] is a patient and compassionate person, tirelessly working to improve the health and well-being of the community.
""".strip(),
    """
[female] is a fearless warrior who now finds herself stranded on the island. She is determined to protect her fellow islanders from any dangers they may face. [female] is a natural leader with an indomitable spirit, never shying away from a challenge or the opportunity to defend those in need.
""".strip(),
    """
[male] is a skillful hunter who woke up on the island without any recollection of his past life. He uses his keen instincts to provide food for the community and is always on the lookout for potential threats. [male] is a solitary individual who finds solace in nature but is willing to work with others to ensure their collective survival.
""".strip(),
    """
[female] is a gifted bard who seeks to bring joy and hope to the island's inhabitants with her enchanting music and stories. She is a beacon of light in these uncertain times, using her talents to lift the spirits of those around her. [female] is a kind and empathetic soul, always willing to lend a listening ear or offer comforting words to those in need.
""".strip(),
]


def generate(prompt: str, system_content: str | None = None) -> str:
    messages: list[dict[str, str]] = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    messages.append({"role": "user", "content": prompt})

    print(f"[Prompt]: {prompt}\n")

    completion: Any = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    return completion.choices[0].message.content


hardcoded_identity_index = 0


def generate_identitiy(gender: str, name: str, dumb: bool = cost_saving_mode) -> str:
    if dumb:
        global hardcoded_identity_index
        hardcoded_identity_index += 1
        return (
            hardcoded_identities[hardcoded_identity_index % len(hardcoded_identities)]
            .replace("[female]", name)
            .replace("[male]", name)
        )

    prompt = get_identity_prompt(gender, name)
    return generate(prompt)


def generate_reflection(name: str, observationLog: ObservationLog, dumb: bool = cost_saving_mode) -> str:
    # if dumb:
    #    return ""

    prompt = get_reflection_prompt(name, observationLog)
    return generate(prompt)


if __name__ == "__main__":
    identity = generate_identitiy("male", "Mythos O'Conner", False)
    print("[Result]: ", identity)
