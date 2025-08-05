from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COHERE_API_KEY: str
    MONGO_URI: str
    MONGODB_DATABASE: str

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()
