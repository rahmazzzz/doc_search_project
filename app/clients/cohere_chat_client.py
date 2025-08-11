import cohere
from typing import List

class CohereChatClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = cohere.Client(api_key)

    def chat(self, message: str, documents: List[dict] = None, system: str = "") -> str:
        """
        Chat with Cohere's LLM.
        'documents' is an optional list of dicts with a 'text' key.
        """
        try:
            response = self.client.chat(
                message=message,
                documents=documents,
                preamble=system  # System prompt in Cohere
            )
            return response.text
        except Exception as e:
            raise ValueError(f"Cohere chat failed: {str(e)}")
