"""Google Cloud Storage service for file uploads"""
from google.cloud import storage
from pathlib import Path
from typing import Optional
import uuid
from PIL import Image
import io
import os

from app.core.config import settings


class StorageService:
    """Service for handling file uploads to Google Cloud Storage"""

    def __init__(self):
        # Initialize GCS client
        # In production, this uses Application Default Credentials
        # Locally, it uses GOOGLE_APPLICATION_CREDENTIALS env var
        self.client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.bucket = self.client.bucket(self.bucket_name)
        self.base_url = f"https://storage.googleapis.com/{self.bucket_name}"

        # Image sizes for variants
        self.image_sizes = {
            "thumbnail": (150, 150),
            "small": (300, 300),
            "medium": (600, 600),
            "large": (1200, 1200),
        }

    def upload_image(self, file_content: bytes, filename: str, content_type: str) -> dict:
        """
        Upload image to GCS and create variants

        Args:
            file_content: Raw file bytes
            filename: Original filename
            content_type: MIME type

        Returns:
            Dictionary with URLs for original and variants
        """
        # Generate unique filename
        ext = filename.split(".")[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"

        # Open image with Pillow
        image = Image.open(io.BytesIO(file_content))

        # Convert RGBA to RGB if necessary
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Upload original
        original_path = f"uploads/{unique_filename}"
        blob = self.bucket.blob(original_path)
        blob.upload_from_string(file_content, content_type=content_type)
        blob.make_public()

        variants = {
            "original": f"/{original_path}"
        }

        # Create and upload variants
        for size_name, dimensions in self.image_sizes.items():
            variant_img = image.copy()
            variant_img.thumbnail(dimensions, Image.Resampling.LANCZOS)

            # Save to bytes
            buffer = io.BytesIO()
            variant_img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)

            # Upload variant
            name_parts = unique_filename.rsplit(".", 1)
            variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
            variant_path = f"uploads/{variant_filename}"

            variant_blob = self.bucket.blob(variant_path)
            variant_blob.upload_from_string(
                buffer.getvalue(), content_type="image/jpeg")
            variant_blob.make_public()

            variants[size_name] = f"/{variant_path}"

        return {
            "filename": unique_filename,
            "url": variants["original"],
            "variants": variants
        }

    def delete_image(self, filename: str) -> bool:
        """
        Delete image and its variants from GCS

        Args:
            filename: Filename to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete original
            blob = self.bucket.blob(f"uploads/{filename}")
            if blob.exists():
                blob.delete()

            # Delete variants
            name_parts = filename.rsplit(".", 1)
            for size_name in self.image_sizes.keys():
                variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
                variant_blob = self.bucket.blob(f"uploads/{variant_filename}")
                if variant_blob.exists():
                    variant_blob.delete()

            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Singleton instance
storage_service = StorageService()
