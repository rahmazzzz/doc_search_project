from fastapi import APIRouter, UploadFile, File, Depends
from tempfile import NamedTemporaryFile
import logging

from app.container.core_container import container
from app.security.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Handles PDF file uploads for the authenticated user.
    Delegates validation, saving, and processing to the service layer.
    """
    username = user.get("username")
    logger.info("Received file upload from user: %s", username)

    # Save uploaded file temporarily
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    logger.debug("Temporary file saved at: %s", tmp_path)

    # Service handles all validation & exceptions
    file_id = await container.file_processing_service.process_upload(
        file_path=tmp_path,
        file_name=file.filename,
        username=username
    )

    logger.info("File processed successfully for user: %s, file_id: %s", username, file_id)
    return {
        "message": "File uploaded and processed successfully",
        "file_id": str(file_id)}
    

    

@router.get("/files")
async def get_all_file(current_user: dict = Depends(get_current_user)):
    files = await container.mongo_repository.get_all_files_metadata()
    return {"files": files}
