# app/clients/mistral_chat_client.py
from typing import List, Optional
from pydantic import BaseModel
import os
from mistralai import Mistral
import logging
from app.clients.llm_interface import LLMChatInterface

logger = logging.getLogger(__name__)

class MistralChatResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = []  # For RAG documents
    language: str = "english"

class MistralChatClient(LLMChatInterface):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required.")
        self.model_name = "ministral-8b-latest"
        self.client = Mistral(api_key=self.api_key)

    async def chat(
        self,
        user: str,
        system: Optional[str] = None
    ) -> MistralChatResponse:
        try:
            # Mistral returns the parsed response directly
            print("LLM will answer")
            response = self.client.chat.parse(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": system
                    },
                    {
                        "role": "user", 
                        "content": user
                    },
                ],
                response_format=MistralChatResponse,
                max_tokens=512,
                temperature=0
            )
            print("response****************", response)
            return response
        except Exception as e:
            logger.exception("Mistral API request failed")
            raise e
