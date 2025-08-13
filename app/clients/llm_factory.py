from typing import Type
from app.core.config import settings
from app.clients.llm_interface import LLMChatInterface
from app.clients.cohere_chat_client import CohereChatClient
from app.clients.openai_chat_client import OpenAIChatClient

class LLMChatFactory:
    _PROVIDERS: dict[str, Type[LLMChatInterface]] = {
        "cohere": CohereChatClient,
        "openai": OpenAIChatClient,
    }

    @classmethod
    def get_client(cls, provider_name: str) -> LLMChatInterface:
        if not provider_name:
            raise ValueError("LLM provider name is required.")

        provider_key = provider_name.lower().strip()
        if provider_key not in cls._PROVIDERS:
            raise ValueError(f"Unknown LLM provider: '{provider_name}'")

        api_keys = {
            "cohere": settings.COHERE_API_KEY,
            "openai": settings.OPENAI_API_KEY,
        }
        api_key = api_keys.get(provider_key)
        if not api_key:
            raise ValueError(f"API key for '{provider_name}' is missing.")

        return cls._PROVIDERS[provider_key](api_key=api_key)
