from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from tempfile import NamedTemporaryFile
import logging

from app.container.core_container import container
from app.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    logger.info("Received file upload from user: %s", user["username"])

    try:
        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        logger.info("Temporary file saved at: %s", tmp_path)
    except Exception as e:
        logger.exception("Failed to save uploaded file")
        raise HTTPException(status_code=500, detail="Failed to save file.")

    try:
        # Delegate all processing to llm_service
        file_id = await container.llm_service.process_upload(
            file_path=tmp_path,
            file_name=file.filename,
            username=user["username"]
        )
    except Exception as e:
        logger.exception("Error during file processing")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    return {
        "message": "File uploaded and processed successfully",
        "file_id": str(file_id)
    }
