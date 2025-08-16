import cohere
from typing import List, Dict, Optional
from .llm_interface import LLMChatInterface

class CohereChatClient(LLMChatInterface):
    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        documents: Optional[List[dict]] = None
    ) -> str:
        """
        Multi-turn chat using Cohere's Chat API.
        """
        try:
            # Use "message" for Cohere format
            latest_message = messages[-1].get("message") or messages[-1].get("content")

            # Cohere expects lowercase role: "USER" -> "user", "CHATBOT" -> "assistant"
            chat_history = []
            for msg in messages[:-1]:
                if "message" in msg:
                    chat_history.append({
                        "role": msg["role"].lower() if msg["role"] in ("user", "assistant") else msg["role"],
                        "message": msg["message"]
                    })
                elif "content" in msg:
                    chat_history.append({
                        "role": msg["role"].lower() if msg["role"] in ("user", "assistant") else msg["role"],
                        "message": msg["content"]
                    })

            response = self.client.chat(
                message=latest_message,
                chat_history=chat_history,
                documents=documents,
                preamble=system or ""
            )

            return response.text

        except Exception as e:
            raise ValueError(f"Cohere chat failed: {str(e)}")
