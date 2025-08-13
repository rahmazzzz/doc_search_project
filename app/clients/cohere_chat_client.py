import cohere
from typing import List, Optional
from .llm_interface import LLMChatInterface

class CohereChatClient(LLMChatInterface):
    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)

    def chat(self, message: str, documents: Optional[List[dict]] = None, system: str = "") -> str:
        try:
            response = self.client.chat(
                message=message,
                documents=documents,
                preamble=system
            )
            return response.text
        except Exception as e:
            raise ValueError(f"Cohere chat failed: {str(e)}")
