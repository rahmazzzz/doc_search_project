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

    def chat(self, message: str, documents: List[dict]) -> str:
        """
        Chat with Cohere using the retrieved context documents.
        Each document is a dict with a "text" key.
        """
        try:
            response = self.client.chat(
                message=message,
                documents=documents
            )
            return response.text
        except Exception as e:
            raise ValueError(f"Cohere chat failed: {str(e)}")
