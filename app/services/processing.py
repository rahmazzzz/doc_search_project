from typing import List
import fitz  # PyMuPDF
import logging
from langchain.text_splitter import CharacterTextSplitter

from app.clients.cohere_client import CohereEmbeddingClient
from app.services.mongo_service import MongoService
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(
        self,
        mongo_service: MongoService,
        qdrant_service: QdrantService,
        cohere_client: CohereEmbeddingClient
    ):
        self.mongo_service = mongo_service
        self.qdrant_service = qdrant_service
        self.cohere_client = cohere_client
        self.splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=50
        )

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract raw text from a PDF file."""
        logger.info(f"Extracting text from PDF: {file_path}")
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise

    def split_text(self, content: str) -> List[str]:
        """Split large text into smaller chunks."""
        logger.info("Splitting text into chunks...")
        return self.splitter.split_text(content)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text chunks using Cohere."""
        try:
            logger.info("Embedding %d text chunks with Cohere", len(texts))
            return self.cohere_client.embed(texts)
        except Exception as e:
            logger.error(f"Failed to embed texts with Cohere: {e}")
            raise

    def answer_question(self, user_id: str, question: str) -> dict:
        """Answer a question by searching relevant chunks and prompting Cohere."""
        try:
            # 1. Embed the user's question
            question_embedding = self.embed_texts([question])[0]

            # 2. Search Qdrant for top matching chunks
            results = self.qdrant_service.search(query_vector=question_embedding, top_k=5)
            if not results:
                return {"error": "No relevant chunks found to answer the question."}

            # 3. Combine top chunks into a context
            context = "\n".join([doc.payload["text"] for doc in results])

            # 4. Generate answer using Cohere LLM
            response = self.cohere_client.client.generate(
                prompt=f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {question}\nAnswer:",
                model="command-r-plus",
                max_tokens=300,
                temperature=0.5
            )
            answer = response.generations[0].text.strip()
            return {"answer": answer}

        except Exception as e:
            logger.error(f"Failed to process question: {e}")
            return {"error": f"Failed to process question: {str(e)}"}