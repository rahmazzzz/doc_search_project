from fastapi import APIRouter, UploadFile, Depends, HTTPException, File
from app.services.file_loader import extract_text_and_chunks
from app.clients.mongo_client import MongoClient
from app.services.embedding import embed_chunks
from app.clients.qdrant_client import upsert_embeddings
from app.auth.deps import get_current_user
import logging

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

@router.post("/", summary="Upload and index a document")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="File is empty")

        chunks = extract_text_and_chunks(file_bytes)
        if not chunks:
            raise HTTPException(status_code=400, detail="No text found in the file")

        for chunk in chunks:
            chunk["uploaded_by"] = user["username"]

        mongo = MongoClient()
        inserted_chunks = await mongo.insert_chunks(chunks)
        if not inserted_chunks:
            raise HTTPException(status_code=500, detail="Failed to insert chunks into database")

        embeddings = embed_chunks(inserted_chunks)
        if not embeddings:
            raise HTTPException(status_code=500, detail="Failed to create embeddings")

        success = upsert_embeddings(embeddings)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upsert embeddings")

        return {
            "message": "File uploaded and indexed successfully",
            "uploaded_by": user["username"],
            "chunks_indexed": len(inserted_chunks)
        }
    except Exception as e:
        logging.exception("Upload failed")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
