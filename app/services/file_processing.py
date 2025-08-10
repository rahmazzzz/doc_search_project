import fitz  # PyMuPDF
import logging
from app.services.mongo_service import MongoService
from app.services.semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(
        self, 
        mongo_service: MongoService,
        semantic_search_service: SemanticSearchService,
    ):
        self.mongo_service = mongo_service
        self.semantic_search_service = semantic_search_service

    def extract_text_from_pdf(self, file_path: str) -> str:
        logger.info(f"Extracting text from PDF: {file_path}")
        try:
            doc = fitz.open(file_path)
            return "".join([page.get_text() for page in doc])
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise

    async def process_upload(self, file_path: str, file_name: str, username: str):
        logger.info(f"Processing upload for file: {file_name} by user: {username}")

        # Extract raw text from the PDF file
        text = self.extract_text_from_pdf(file_path)
        if not text:
            logger.warning("No text extracted from PDF.")
            raise ValueError("Uploaded PDF contains no text.")

        # Split text into chunks
        chunks = self.semantic_search_service.split_text(text)
        if not chunks:
            logger.warning("No chunks created from text.")
            raise ValueError("Failed to split text into chunks.")

        # Embed chunks (async)
        embeddings = await self.semantic_search_service.embed_texts(chunks)
        if not embeddings:
            logger.warning("No embeddings generated.")
            raise ValueError("Failed to embed text chunks.")

        # Metadata for storing vectors
        metadata = {
            "username": username,
            "filename": file_name
        }

        # Store embeddings and chunks as vectors in Qdrant
        await self.semantic_search_service.store_vectors(embeddings, chunks, metadata)

        # Save file metadata in MongoDB
        file_data = {
            "filename": file_name,
            "username": username,
        }
        file_id = await self.mongo_service.save_file(file_data)
        logger.info(f"File metadata saved with ID: {file_id}")

        return file_id
