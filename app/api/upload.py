from fastapi import APIRouter, UploadFile
from app.services.file_loader import extract_text_and_chunks
from app.services.mongo_client import insert_chunks
from app.services.embedding import embed_chunks
from app.services.qdrant_client import upsert_embeddings

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile):
    file_bytes = await file.read()
    chunks = extract_text_and_chunks(file_bytes)
    inserted_chunks = insert_chunks(chunks)
    embeddings = embed_chunks(inserted_chunks)
    upsert_embeddings(embeddings)
    return {"message": "Uploaded & indexed"}
