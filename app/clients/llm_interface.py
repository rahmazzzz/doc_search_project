from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class LLMChatInterface(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        documents: Optional[List[dict]] = None
    ) -> str:
        """
        Multi-turn chat with an LLM.

        Args:
            messages: Conversation history as a list of dicts 
                      [{"role": "user"/"assistant"/"system", "content": str}]
            system: Optional system message to guide behavior.
            documents: Optional retrieved documents for context (RAG).

        Returns:
            Assistant's reply as a string.
        """
        pass


