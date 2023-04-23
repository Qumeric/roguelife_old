# ruff: noqa: E501

from chromadb.utils import embedding_functions  # type: ignore

from components.observation_log import Observation
from constants import chroma_client
from env import openai_api_key

if __name__ == "__main__":
    generate_embeddings = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,  # type: ignore
    )

    collection = chroma_client.create_collection(
        name="sample_collection",
        embedding_function=generate_embeddings,
    )

    example_observation = Observation("This is a test observation.", None)
    important_observation = Observation("This is a important observation.", None)
    duck_observation = Observation("I see a cute duck.", None)

    obs_texts = [example_observation.text, important_observation.text, duck_observation.text]

    collection.add(
        embeddings=generate_embeddings(obs_texts),
        documents=obs_texts,
        ids=["1", "2", "3"],
    )

    results = collection.query(
        query_embeddings=generate_embeddings(["Something about ducks", "Important stuff"]),
        n_results=1,
    )

    print(f"Results: {results}")
