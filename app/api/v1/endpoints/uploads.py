from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List

from app.api.deps import get_current_admin
from app.models.user import User
from app.services.storage_service import storage_service

router = APIRouter()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> None:
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )


@router.post("/upload", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin)
):
    """Upload a single image. Admin only."""
    validate_image(file)
    try:
        file_content = await file.read()
        result = storage_service.upload_image(
            file_content=file_content,
            filename=file.filename or "upload.jpg",
            content_type=file.content_type or "image/jpeg",
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/upload-multiple", response_model=List[dict])
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_admin)
):
    """Upload multiple images (max 10). Admin only."""
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload"
        )
    results = []
    for file in files:
        try:
            validate_image(file)
            file_content = await file.read()
            result = storage_service.upload_image(
                file_content=file_content,
                filename=file.filename or "upload.jpg",
                content_type=file.content_type or "image/jpeg",
            )
            results.append(result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process {file.filename}: {str(e)}"
            )
    return results


@router.delete("/delete/{filename}")
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_admin)
):
    """Delete an uploaded image and its variants. Admin only."""
    success = storage_service.delete_image(filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
    return {"message": "File deleted successfully"}
