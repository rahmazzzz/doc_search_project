from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str
    MONGODB_DATABASE: str

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str

    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # LLM provider settings
    LLM_PROVIDER: str | None = None # "cohere" or "openai"
    COHERE_API_KEY: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
