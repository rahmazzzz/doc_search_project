from typing import List
from langchain.text_splitter import CharacterTextSplitter
import fitz  # PyMuPDF
import logging
from app.clients.cohere_client import CohereEmbeddingClient  # import your wrapper

logger = logging.getLogger(__name__)

class ProcessingService:
    def __init__(self, cohere_client: CohereEmbeddingClient):
        self.splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=50
        )
        self.cohere_client = cohere_client  # use injected wrapper

    def split_text(self, content: str) -> List[str]:
        logger.info("Splitting text into chunks...")
        return self.splitter.split_text(content)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.info("Calling Cohere to embed %d text chunks", len(texts))
            return self.cohere_client.embed(texts)
        except Exception as e:
            logger.error(f"Failed to embed texts with Cohere: {e}")
            raise

    def extract_text_from_pdf(self, file_path: str) -> str:
        logger.info(f"Extracting text from PDF: {file_path}")
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text