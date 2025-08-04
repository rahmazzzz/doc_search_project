from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # External API keys
    COHERE_API_KEY: str
    SECRET_KEY: str  # used for JWT token signing
    JWT_ALGORITHM: str = "HS256"  # default algorithm

    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "mydb"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "my_collection"

    class Config:
        env_file = ".env"

# Global instance
settings = Settings()


