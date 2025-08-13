import openai
from typing import List, Optional
from app.clients.llm_interface import LLMChatInterface

class OpenAIChatClient(LLMChatInterface):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def chat(self, message: str, documents: Optional[List[dict]] = None, system: str = "") -> str:
        """
        Uses the new OpenAI SDK (>=1.0.0) chat interface.
        Matches the CohereChatClient interface.
        """
        try:
            # Combine documents into context string
            context = ""
            if documents:
                context = "\n\n".join([doc.get("text", "") for doc in documents])

            user_message = f"{message}\n\nContext:\n{context}" if context else message

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            raise ValueError(f"OpenAI chat failed: {str(e)}")
