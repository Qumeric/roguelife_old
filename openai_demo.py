# type: ignore
import os

from dotenv import load_dotenv
import openai

load_dotenv()
openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_SK")

# print(openai.Model.list())

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a human living in a fantasy world who discovered himself on an island.\
Another human named Gord approached you.",
        },
        {"role": "user", "content": "Hi! I'm new here. What's your name?"},
        # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    ],
)

print(completion)
