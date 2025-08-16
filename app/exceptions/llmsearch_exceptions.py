from .base_exceptions import ServiceError, ExternalServiceError

class PromptNotFoundError(ServiceError):
    """Raised when a prompt template is missing."""
    def __init__(self, prompt_name: str):
        super().__init__(detail=f"No prompt found with name '{prompt_name}'", status_code=404)

class ChatHistoryRetrievalError(ExternalServiceError):
    """Raised when retrieving chat history fails."""
    def __init__(self, detail: str = "Failed to retrieve chat history"):
        super().__init__(detail=detail)

class ContextRetrievalError(ExternalServiceError):
    """Raised when retrieving semantic search context fails."""
    def __init__(self, detail: str = "Failed to retrieve context for LLM prompt"):
        super().__init__(detail=detail)

class LLMProviderError(ExternalServiceError):
    """Raised when an LLM provider call fails."""
    def __init__(self, provider: str, message: str = "LLM provider call failed"):
        super().__init__(detail=f"{provider}: {message}")

class ChatHistorySaveError(ExternalServiceError):
    """Raised when saving updated chat history fails."""
    def __init__(self, detail: str = "Failed to save chat history"):
        super().__init__(detail=detail)
