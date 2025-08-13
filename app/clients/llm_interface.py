from abc import ABC, abstractmethod

class LLMChatInterface(ABC):
    @abstractmethod
    async def chat(
        self, user_id: str, question: str, file_id: str, prompt_name: str
    ) -> dict:
        """
        Standard method for answering a question given:
        - user_id
        - question text
        - file_id to search in
        - prompt_name (for selecting prompt templates)
        Returns a dict with either {'answer': str} or {'error': str}.
        """
        pass

