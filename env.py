import os

from dotenv import load_dotenv

load_dotenv()
openai_organization: str = os.getenv("OPENAI_ORG", "ADD OPENAI ORGANIZATION TO ENV")
openai_api_key: str = os.getenv("OPENAI_API_KEY", "ADD OPENAI SECRET KEY TO ENV")
