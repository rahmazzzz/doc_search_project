import openai
from typing import List, Dict, Optional
from app.clients.llm_interface import LLMChatInterface

class OpenAIChatClient(LLMChatInterface):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        documents: Optional[List[dict]] = None
    ) -> str:
        """
        Multi-turn chat using OpenAI's API with support for optional RAG context.
        """
        try:
            # Append RAG context to the latest user message if provided
            if documents:
                context_text = "\n\n".join([doc.get("text", "") for doc in documents])
                messages[-1]["content"] += f"\n\nContext:\n{context_text}"

            # Insert system message at start if provided
            final_messages = []
            if system:
                final_messages.append({"role": "system", "content": system})
            final_messages.extend(messages)

            # OpenAI SDK >= 1.0.0 async call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=final_messages,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            raise ValueError(f"OpenAI chat failed: {str(e)}")
