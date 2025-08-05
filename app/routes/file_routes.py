from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from tempfile import NamedTemporaryFile
from app.container.core_container import container
from app.deps import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Save file to temp location
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract and embed text
    try:
        text = container.processing_service.extract_text_from_pdf(tmp_path)
        chunks = container.processing_service.split_text(text)
        embeddings = container.processing_service.embed_texts(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    # Prepare metadata with user from token
    metadata = [{"text": chunk, "username": user["username"]} for chunk in chunks]
    container.qdrant_service.insert_vectors(embeddings, metadata)

    # Save file info to Mongo
    file_id = await container.mongo_service.save_file({
        "filename": file.filename,
        "username": user["username"]
    })

    return {
        "message": "File uploaded and processed successfully",
        "file_id": str(file_id)
    }
