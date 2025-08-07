import fitz  # PyMuPDF
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.mongo_service import MongoService


class LLMService:
    def __init__(
        self,
        qdrant_service: QdrantService,
        cohere_client,
        embedding_service: EmbeddingService,
        mongo_service: MongoService = None  # Optional injection
    ):
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
        self.mongo_service = mongo_service
        self.cohere_client = cohere_client

    def extract_text_from_pdf(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        return " ".join([page.get_text() for page in doc])

    def split_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))
            start += chunk_size - overlap
        return chunks

    async def process_upload(self, file_path: str, file_name: str, username: str):
        text = self.extract_text_from_pdf(file_path)
        chunks = self.split_text(text)
        embeddings = self.embedding_service.embed_texts(chunks)

        metadata = [{"text": chunk, "username": username} for chunk in chunks]
        self.qdrant_service.insert_vectors(embeddings, metadata)

        file_id = await self.mongo_service.save_file({
            "filename": file_name,
            "username": username
        })

        return file_id

    async def semantic_search(self, query: str, username: str) -> list[dict]:
        embedding = self.embedding_service.embed_texts([query])[0]
        results = self.qdrant_service.search(embedding, username=username)

        return [
            {
                "score": hit.score,
                "text": hit.payload["text"],
                "file_id": hit.payload.get("file_id"),
                "filename": hit.payload.get("filename"),
            }
            for hit in results
        ]

    async def answer_question(self, user_id: str, question: str) -> dict:
        try:
            embedding = self.embedding_service.embed_texts([question])[0]
            search_results = self.qdrant_service.search(embedding, username=user_id)

            if not search_results:
                return {"error": "No relevant context found for the question."}

            context = "\n".join([hit.payload["text"] for hit in search_results[:3]])

            response =  self.cohere_client.chat(
                message=question,
                documents=[{"text": context}]
            )

            return {"answer": response}

        except Exception as e:
            return {"error": f"Failed to answer question: {str(e)}"}