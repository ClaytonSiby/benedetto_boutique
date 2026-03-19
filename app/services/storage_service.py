"""Cloudinary storage service for file uploads"""
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from pathlib import Path
from typing import Optional
import uuid
from PIL import Image
import io

from app.core.config import settings


class StorageService:
    """Service for handling file uploads to Cloudinary or local storage"""

    def __init__(self):
        self.use_cloudinary = settings.USE_CLOUDINARY

        if self.use_cloudinary:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
        else:
            self.local_upload_dir = Path("uploads")
            self.local_upload_dir.mkdir(exist_ok=True)

        # Image sizes used for local variant generation only
        self.image_sizes = {
            "thumbnail": (150, 150),
            "small": (300, 300),
            "medium": (600, 600),
            "large": (1200, 1200),
        }

    def upload_image(self, file_content: bytes, filename: str, content_type: str) -> dict:
        """
        Upload image to Cloudinary or local storage.

        Returns:
            Dictionary with filename, url, and variants dict.
        """
        ext = filename.split(".")[-1].lower()
        unique_id = str(uuid.uuid4())

        if self.use_cloudinary:
            public_id = f"b-boutique/{unique_id}"
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                resource_type="image",
                quality="auto",
                fetch_format="auto",
            )
            base_url = result["secure_url"]
            variants = {
                "original": base_url,
                "thumbnail": cloudinary.utils.cloudinary_url(
                    public_id, width=150, height=150, crop="fill",
                    quality="auto", fetch_format="auto"
                )[0],
                "small": cloudinary.utils.cloudinary_url(
                    public_id, width=300, height=300, crop="fill",
                    quality="auto", fetch_format="auto"
                )[0],
                "medium": cloudinary.utils.cloudinary_url(
                    public_id, width=600, height=600, crop="fill",
                    quality="auto", fetch_format="auto"
                )[0],
                "large": cloudinary.utils.cloudinary_url(
                    public_id, width=1200, height=1200, crop="limit",
                    quality="auto", fetch_format="auto"
                )[0],
            }
            return {
                "filename": unique_id,
                "url": base_url,
                "variants": variants,
            }

        # Local storage fallback
        unique_filename = f"{unique_id}.{ext}"
        image = Image.open(io.BytesIO(file_content))
        if image.mode == "RGBA":
            image = image.convert("RGB")

        local_file_path = self.local_upload_dir / unique_filename
        with open(local_file_path, "wb") as f:
            f.write(file_content)

        variants = {"original": f"/uploads/{unique_filename}"}
        for size_name, dimensions in self.image_sizes.items():
            variant_img = image.copy()
            variant_img.thumbnail(dimensions, Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            variant_img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)
            name_parts = unique_filename.rsplit(".", 1)
            variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
            local_variant_path = self.local_upload_dir / variant_filename
            with open(local_variant_path, "wb") as f:
                f.write(buffer.getvalue())
            variants[size_name] = f"/uploads/{variant_filename}"

        return {
            "filename": unique_filename,
            "url": f"/uploads/{unique_filename}",
            "variants": variants,
        }

    def delete_image(self, filename: str) -> bool:
        """
        Delete image from Cloudinary or local storage.

        Args:
            filename: UUID string (Cloudinary) or filename with extension (local).
        """
        try:
            if self.use_cloudinary:
                public_id = f"b-boutique/{filename}"
                cloudinary.uploader.destroy(public_id, resource_type="image")
            else:
                local_upload_dir = Path("uploads")
                local_file = local_upload_dir / filename
                if local_file.exists():
                    local_file.unlink()
                name_parts = filename.rsplit(".", 1)
                for size_name in self.image_sizes.keys():
                    variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
                    local_variant = local_upload_dir / variant_filename
                    if local_variant.exists():
                        local_variant.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Singleton instance
storage_service = StorageService()
