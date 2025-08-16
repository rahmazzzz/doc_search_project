import fitz  # PyMuPDF
import logging
from app.repositories.mongo_repository import MongoRepository
from app.services.semantic_search import SemanticSearchService
from app.exceptions.file_exceptions import (
    PDFExtractionException,
    EmptyPDFTextException,
    ChunkCreationException,
    EmbeddingGenerationException,
    FileRetrievalException
)

logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self, mongo_repository: MongoRepository, semantic_search_service: SemanticSearchService):
        self.mongo_repository = mongo_repository
        self.semantic_search_service = semantic_search_service

    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            text = "".join([page.get_text() for page in doc])
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise PDFExtractionException()

    async def process_upload(self, file_path: str, file_name: str, user_id: str, username: str):
        logger.info(f"Uploading file '{file_name}' for user '{username}'")
        
        try:
            # Step 0 - Save file
            file_id = await self.mongo_repository.save_file(file_path, file_name, user_id, username)
            
            # Step 1 - Extract text
            text = self.extract_text_from_pdf(file_path)
            if not text:
                raise EmptyPDFTextException()

            # Step 2 - Split text
            chunks = self.semantic_search_service.split_text(text)
            if not chunks:
                raise ChunkCreationException()

            # Step 3 - Generate embeddings
            embeddings = await self.semantic_search_service.embed_texts(chunks)
            if not embeddings:
                raise EmbeddingGenerationException()

            # Step 4 - Store in Qdrant
            metadata = {"username": username, "user_id": user_id, "filename": file_name}
            chunks_payloads = [{"text": chunk, **metadata, "file_id": str(file_id)} for chunk in chunks]
            await self.semantic_search_service.store_vectors(
                embeddings,
                chunks_payloads,
                file_id=str(file_id),
                metadata=metadata
            )

            return file_id

        except (EmptyPDFTextException, ChunkCreationException, EmbeddingGenerationException, PDFExtractionException):
            raise  # Re-raise known exceptions directly
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise FileRetrievalException()

    async def get_all_file_ids(self) -> list:
        try:
            return await self.mongo_repository.get_all_file_ids()
        except Exception as e:
            logger.error(f"Failed to retrieve file IDs: {e}")
            raise FileRetrievalException()
