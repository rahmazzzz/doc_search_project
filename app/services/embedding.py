import fitz  # PyMuPDF
import logging
from typing import List
from langchain.text_splitter import CharacterTextSplitter
from app.clients.cohere_client import CohereEmbeddingClient

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, cohere_client: CohereEmbeddingClient):
        self.cohere_client = cohere_client
        self.splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=50
        )

    def extract_text_from_pdf(self, file_path: str) -> str:
        logger.info(f"Extracting text from PDF: {file_path}")
        try:
            doc = fitz.open(file_path)
            return "".join([page.get_text() for page in doc])
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise

    def split_text(self, content: str) -> List[str]:
        logger.info("Splitting text into chunks...")
        return self.splitter.split_text(content)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.info("Embedding %d text chunks with Cohere", len(texts))
            return self.cohere_client.embed(texts)
        except Exception as e:
            logger.error(f"Failed to embed texts with Cohere: {e}")
            raise