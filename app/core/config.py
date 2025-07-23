from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# ✅ Force .env to load first
load_dotenv()

print("DEBUG .env COHERE_API_KEY:", os.getenv("COHERE_API_KEY"))

class Settings(BaseSettings):
    COHERE_API_KEY: str
    MONGO_URI: str = "mongodb://localhost:27017"
    QDRANT_URL: str = "http://localhost:6333"

    class Config:
        env_file = ".env"

settings = Settings()
