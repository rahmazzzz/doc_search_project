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

    async def delete_user_vectors(self, username: str):
        """Remove all existing vectors for the given user from Qdrant."""
        logger.info(f"Deleting existing vectors for user: {username}")
        q_filter = Filter(
            must=[
                FieldCondition(
                    key="username",
                    match=MatchValue(value=username)
                )
            ]
        )
        try:
            self.semantic_search_service.qdrant_repository.delete_vectors(q_filter)
            logger.info(f"Successfully deleted old vectors for user: {username}")
        except Exception as e:
            logger.error(f"Failed to delete old vectors for user {username}: {e}")
            raise

    async def process_upload(self, file_path: str, file_name: str, username: str):
        """
        Process a PDF upload:
        1. Delete any old vectors for the user
        2. Extract text
        3. Split into chunks
        4. Embed chunks
        5. Store vectors in Qdrant
        6. Save metadata in MongoDB
        """
        logger.info(f"Starting file upload process for '{file_name}' by user '{username}'")

        # 1. Remove old vectors for this user
        await self.delete_user_vectors(username)

        # 2. Extract raw text from the PDF
        text = self.extract_text_from_pdf(file_path)
        if not text:
            logger.warning("No text extracted from PDF.")
            raise ValueError("Uploaded PDF contains no extractable text.")

        # 3. Split text into smaller chunks
        chunks = self.semantic_search_service.split_text(text)
        if not chunks:
            logger.warning("No chunks created from text.")
            raise ValueError("Failed to split text into chunks.")

        # 4. Embed chunks asynchronously
        embeddings = await self.semantic_search_service.embed_texts(chunks)
        if not embeddings:
            logger.warning("No embeddings generated.")
            raise ValueError("Failed to embed text chunks.")

        # 5. Store embeddings and chunks in Qdrant
        metadata = {"username": username, "filename": file_name}
        await self.semantic_search_service.store_vectors(embeddings, chunks, metadata)
        logger.info(f"Stored {len(chunks)} chunks as vectors for user '{username}'")

        # 6. Save file metadata in MongoDB
        file_data = {"filename": file_name, "username": username}
        file_id = await self.mongo_repository.save_file(file_data)
        logger.info(f"File metadata saved in MongoDB with ID: {file_id}")

        return file_id
