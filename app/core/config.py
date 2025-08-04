from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # --- External APIs ---
    COHERE_API_KEY: str = Field(..., description="API key for Cohere")

    # --- JWT Auth ---
    SECRET_KEY: str = Field(..., description="Secret key for signing JWT tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm to use")

    # --- MongoDB ---
    MONGO_URI: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URI")
    MONGODB_DATABASE: str = Field(default="mydb", description="MongoDB database name")

    # --- Qdrant ---
    QDRANT_URL: str = Field(default="http://localhost:6333", description="Qdrant vector database URL")
    QDRANT_COLLECTION: str = Field(default="my_collection", description="Qdrant collection name")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  



settings = Settings()
