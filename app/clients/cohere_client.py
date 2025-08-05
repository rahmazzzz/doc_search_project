import cohere
from typing import List

class CohereEmbeddingClient:
    def __init__(self, api_key: str, model: str = "embed-english-v3.0", input_type: str = "search_document"):
        self.api_key = api_key
        self.model = model
        self.input_type = input_type
        self.client = cohere.Client(api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type=self.input_type
        )
        return response.embeddings
