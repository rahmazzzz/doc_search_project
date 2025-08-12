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
    """
    username = user.get("sub")
    user_id = user.get("user_id")
    logger.info("Received file upload from user: %s (ID: %s)", username, user_id)

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    logger.debug("Temporary file saved at: %s", tmp_path)

    file_id = await container.file_processing_service.process_upload(
        tmp_path,
        file.filename,
        str(user_id),
        username
    )

    logger.info("File processed successfully for user: %s, file_id: %s", username, file_id)
    return {
        "message": "File uploaded and processed successfully",
        "file_id": str(file_id)
    }



@router.get("/files")
async def get_all_files_metadata(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    username = current_user["sub"]  # username is stored in 'sub'

    files_metadata = await container.mongo_repository.get_all_files_metadata(user_id)

    return {
        "owner": {
            "user_id": user_id,
            "username": username
        },
        "files": files_metadata
    }