from fastapi import APIRouter, UploadFile, Depends, HTTPException, File
from app.services.file_loader import extract_text_and_chunks
from app.services.mongo_client import insert_chunks
from app.services.embedding import embed_chunks
from app.services.qdrant_client import upsert_embeddings
from app.auth.deps import get_current_user  # <-- ensures user is authenticated

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

@router.post("/", summary="Upload and index a document")
async def upload_file(
    file: UploadFile = File(...),  # <-- make sure FastAPI knows this is a file upload
    user: dict = Depends(get_current_user)  # <-- user is extracted from token
):
    file_bytes = await file.read()
    print("File read, size:", len(file_bytes))

    chunks = extract_text_and_chunks(file_bytes)
    print("Chunks extracted:", len(chunks))

    # Attach uploader info to each chunk
    for chunk in chunks:
        chunk["uploaded_by"] = user["username"]  # track which user uploaded this

    inserted_chunks = await insert_chunks(chunks)
    print("Inserted into Mongo:", inserted_chunks)

    embeddings = embed_chunks(inserted_chunks)
    print("Embeddings generated:", len(embeddings))

    upsert_embeddings(embeddings)
    print("Embeddings upserted into Qdrant")

    return {
        "message": "File uploaded and indexed successfully",
        "uploaded_by": user["username"],
        "chunks_indexed": len(inserted_chunks)
    }
