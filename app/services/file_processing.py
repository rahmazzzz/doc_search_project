# file_processing.py

import fitz  # PyMuPDF
import logging
from app.repositories.mongo_repository import MongoRepository
from app.services.semantic_search import SemanticSearchService
from qdrant_client.models import Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(
        self, 
        mongo_repository: MongoRepository,
        semantic_search_service: SemanticSearchService,
    ):
        self.mongo_repository = mongo_repository
        self.semantic_search_service = semantic_search_service

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from a PDF file."""
        logger.info(f"Extracting text from PDF: {file_path}")
        try:
            doc = fitz.open(file_path)
            text = "".join([page.get_text() for page in doc])
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise

    async def process_upload(self, file_path: str, file_name: str, username: str):
        """
        Process a PDF upload:
        0. Save the file content + metadata in MongoDB (as binary + fields)
        1. Extract text
        2. Split into chunks
        3. Embed chunks
        4. Store vectors in Qdrant
        """
        logger.info(f"Starting file upload process for '{file_name}' by user '{username}'")

        # 0. Save the PDF file content + metadata to MongoDB
        file_id = await self.mongo_repository.save_file(file_path, file_name, username)
        logger.info(f"Saved file '{file_name}' content to MongoDB with id {file_id}")

        # 1. Extract raw text from the PDF
        text = self.extract_text_from_pdf(file_path)
        if not text:
            logger.warning("No text extracted from PDF.")
            raise ValueError("Uploaded PDF contains no extractable text.")

        # 2. Split text into smaller chunks
        chunks = self.semantic_search_service.split_text(text)
        if not chunks:
            logger.warning("No chunks created from text.")
            raise ValueError("Failed to split text into chunks.")

        # 3. Embed chunks asynchronously
        embeddings = await self.semantic_search_service.embed_texts(chunks)
        if not embeddings:
            logger.warning("No embeddings generated.")
            raise ValueError("Failed to embed text chunks.")

        # 4. Store embeddings and chunks in Qdrant
        metadata = {"username": username, "filename": file_name}  # metadata without file_id
        chunks_payloads = [{"text": chunk, **metadata, "file_id": str(file_id)} for chunk in chunks]

        await self.semantic_search_service.store_vectors(
            embeddings, 
            chunks_payloads, 
            file_id=str(file_id),
            metadata=metadata
        )
        return file_id

    # New method to get all file IDs
    async def get_all_file_ids(self) -> list:
        """
        Return a list of all file IDs stored in MongoDB.
        """
        try:
            file_ids = await self.mongo_repository.get_all_file_ids()
            return file_ids
        except Exception as e:
            logger.error(f"Failed to get all file IDs: {e}")
            raise
