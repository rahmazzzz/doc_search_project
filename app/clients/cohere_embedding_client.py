import cohere
import logging
from typing import List

logger = logging.getLogger(__name__)

class CohereEmbeddingClient:
    def __init__(
        self,
        api_key: str,
        model: str = "embed-english-v3.0",
        input_type: str = "search_document"
    ):
        logger.info("Initializing CohereEmbeddingClient")
        self.api_key = api_key
        self.model = model
        self.input_type = input_type
        self.client = cohere.Client(api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        Cohere's SDK is synchronous.
        """
        if not texts:
            logger.warning("embed() called with an empty text list")
            return []

        logger.info(f"Generating embeddings for {len(texts)} text chunks")
        preview = texts[0][:100].replace("\n", " ")
        logger.debug(f"First chunk preview: {preview}...")


        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=self.input_type
            )
            logger.info(f"Received {len(response.embeddings)} embeddings from Cohere")
            return response.embeddings
        except Exception as e:
            logger.exception("Error during Cohere embedding request")
            raise
