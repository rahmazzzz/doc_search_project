from fastapi import APIRouter, UploadFile, Depends, HTTPException
from app.services.file_loader import extract_text_and_chunks
from app.services.mongo_client import insert_chunks
from app.services.embedding import embed_chunks
from app.services.qdrant_client import upsert_embeddings
from app.auth.deps import get_current_user

router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile,
    user=Depends(get_current_user)
):
    file_bytes = await file.read()
    print(" File read, size:", len(file_bytes))

    chunks = extract_text_and_chunks(file_bytes)
    print(" Chunks extracted:", len(chunks))

    #  Attach uploader info to each chunk
    for chunk in chunks:
        chunk["uploaded_by"] = user["username"]

    inserted_chunks = await insert_chunks(chunks)
    print("Inserted into Mongo:", inserted_chunks)

    embeddings = embed_chunks(inserted_chunks)
    print(" Embeddings generated:", len(embeddings))

    upsert_embeddings(embeddings)
    print("Embeddings upserted into Qdrant")

    return {"message": "Uploaded & indexed by", "user": user["username"]}
