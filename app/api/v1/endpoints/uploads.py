from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
from pathlib import Path
import uuid
import shutil
from PIL import Image
import io

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

# Configure upload settings
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
IMAGE_SIZES = {
    "thumbnail": (150, 150),
    "small": (300, 300),
    "medium": (600, 600),
    "large": (1200, 1200),
}

# Create upload directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image"""
    # Check file extension
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )


def create_image_variants(image_path: Path, filename: str) -> dict:
    """Create different sized variants of the image"""
    variants = {}

    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == "RGBA":
                img = img.convert("RGB")

            # Create original
            variants["original"] = filename

            # Create sized variants
            for size_name, dimensions in IMAGE_SIZES.items():
                # Calculate new dimensions maintaining aspect ratio
                img_copy = img.copy()
                img_copy.thumbnail(dimensions, Image.Resampling.LANCZOS)

                # Generate filename for variant
                name_parts = filename.rsplit(".", 1)
                variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
                variant_path = UPLOAD_DIR / variant_filename

                # Save variant
                img_copy.save(variant_path, quality=85, optimize=True)
                variants[size_name] = variant_filename

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}"
        )

    return variants


@router.post("/upload", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a single image and create variants.
    Requires authentication. Admin only endpoint.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can upload files"
        )

    # Validate image
    validate_image(file)

    # Generate unique filename
    ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save original file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Create image variants
    variants = create_image_variants(file_path, unique_filename)

    return {
        "filename": unique_filename,
        "url": f"/uploads/{unique_filename}",
        "variants": {
            size: f"/uploads/{filename}"
            for size, filename in variants.items()
        }
    }


@router.post("/upload-multiple", response_model=List[dict])
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple images at once.
    Requires authentication. Admin only endpoint.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can upload files"
        )

    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload"
        )

    results = []
    for file in files:
        try:
            # Validate image
            validate_image(file)

            # Generate unique filename
            ext = file.filename.split(".")[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            file_path = UPLOAD_DIR / unique_filename

            # Save original file
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Create image variants
            variants = create_image_variants(file_path, unique_filename)

            results.append({
                "filename": unique_filename,
                "url": f"/uploads/{unique_filename}",
                "variants": {
                    size: f"/uploads/{filename}"
                    for size, filename in variants.items()
                }
            })
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
    current_user: User = Depends(get_current_user)
):
    """
    Delete an uploaded image and its variants.
    Requires authentication. Admin only endpoint.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete files"
        )

    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    try:
        # Delete original file
        file_path.unlink()

        # Delete variants
        name_parts = filename.rsplit(".", 1)
        for size_name in IMAGE_SIZES.keys():
            variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
            variant_path = UPLOAD_DIR / variant_filename
            if variant_path.exists():
                variant_path.unlink()

        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
