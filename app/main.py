from fastapi import FastAPI
from app.api import upload, search

app = FastAPI(
    title="DocSearch",
    description="Upload documents and search answers from them using LLM and vector search",
    version="1.0.0",
)

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(search.router, prefix="/search", tags=["Search"])
