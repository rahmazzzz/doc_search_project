from .base_exceptions import ServiceError

class TextSplittingException(ServiceError):
    def __init__(self, detail: str = "Failed to split text into chunks"):
        super().__init__(detail=detail)

class EmbeddingFailedException(ServiceError):
    def __init__(self, detail: str = "Failed to generate embeddings"):
        super().__init__(detail=detail)

class VectorStorageException(ServiceError):
    def __init__(self, detail: str = "Failed to store vectors in Qdrant"):
        super().__init__(detail=detail)

class SearchFailedException(ServiceError):
    def __init__(self, detail: str = "Search operation failed"):
        super().__init__(detail=detail)

class VectorInsertionException(ServiceError):
    def __init__(self, detail: str = "Failed to insert vectors into Qdrant"):
        super().__init__(detail=detail)
