from .base_exceptions import ServiceError

class PDFExtractionException(ServiceError):
    def __init__(self, detail: str = "Failed to extract text from the PDF file"):
        super().__init__(detail=detail, status_code=500)

class EmptyPDFTextException(ServiceError):
    def __init__(self, detail: str = "Uploaded PDF contains no extractable text"):
        super().__init__(detail=detail, status_code=400)

class ChunkCreationException(ServiceError):
    def __init__(self, detail: str = "Failed to split text into chunks"):
        super().__init__(detail=detail, status_code=500)

class EmbeddingGenerationException(ServiceError):
    def __init__(self, detail: str = "Failed to embed text chunks"):
        super().__init__(detail=detail, status_code=500)

class FileRetrievalException(ServiceError):
    def __init__(self, detail: str = "Failed to retrieve file IDs and user IDs"):
        super().__init__(detail=detail, status_code=500)
