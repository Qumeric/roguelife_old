import chromadb  # type: ignore

map_width = 160
map_height = 100 + 3

# It will use hardcoded generatations where possible instead of querying llm.
cost_saving_mode = True

chroma_client = chromadb.Client()
