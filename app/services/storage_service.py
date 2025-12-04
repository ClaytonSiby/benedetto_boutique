"""Google Cloud Storage service for file uploads"""
from google.cloud import storage
from pathlib import Path
from typing import Optional
import uuid
from PIL import Image
import io
import os
from datetime import timedelta

from app.core.config import settings


class StorageService:
    """Service for handling file uploads to Google Cloud Storage or local storage"""

    def __init__(self):
        # Lazy initialization - only create GCS client when needed
        self._client = None
        self._bucket = None
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.use_gcs = settings.USE_GCS

        # Local storage path
        self.local_upload_dir = Path("uploads")
        self.local_upload_dir.mkdir(exist_ok=True)

        # Image sizes for variants
        self.image_sizes = {
            "thumbnail": (150, 150),
            "small": (300, 300),
            "medium": (600, 600),
            "large": (1200, 1200),
        }

    @property
    def client(self):
        """Lazy initialization of GCS client"""
        if self.use_gcs and self._client is None:
            self._client = storage.Client(project=settings.GCP_PROJECT_ID)
        return self._client

    @property
    def bucket(self):
        """Lazy initialization of GCS bucket"""
        if self.use_gcs and self._bucket is None:
            self._bucket = self.client.bucket(self.bucket_name)
        return self._bucket

    def get_public_url(self, blob_name: str) -> str:
        """
        Get URL for a blob (direct GCS URL for GCS, direct URL for local).

        Args:
            blob_name: Path to the blob in the bucket or local file

        Returns:
            URL string
        """
        if self.use_gcs:
            # Return direct public GCS URL
            return f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
        else:
            # Return local URL
            return f"/uploads/{blob_name}"

    def upload_image(self, file_content: bytes, filename: str, content_type: str) -> dict:
        """
        Upload image to GCS or local storage and create variants

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

        if self.use_gcs:
            # Upload to GCS
            blob = self.bucket.blob(original_path)
            blob.upload_from_string(file_content, content_type=content_type)
        else:
            # Save locally
            local_file_path = self.local_upload_dir / unique_filename
            with open(local_file_path, "wb") as f:
                f.write(file_content)

        # Get public URLs
        variants = {
            "original": self.get_public_url(original_path)
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

            if self.use_gcs:
                # Upload to GCS
                variant_blob = self.bucket.blob(variant_path)
                variant_blob.upload_from_string(
                    buffer.getvalue(), content_type="image/jpeg")
            else:
                # Save locally
                local_variant_path = self.local_upload_dir / variant_filename
                with open(local_variant_path, "wb") as f:
                    f.write(buffer.getvalue())

            # Get public URL for variant
            variants[size_name] = self.get_public_url(variant_path)

        return {
            "filename": unique_filename,
            "url": variants["original"],
            "variants": variants
        }

    def delete_image(self, filename: str) -> bool:
        """
        Delete image and its variants from GCS or local storage

        Args:
            filename: Filename to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_gcs:
                # Delete from GCS
                blob = self.bucket.blob(f"uploads/{filename}")
                if blob.exists():
                    blob.delete()

                # Delete variants
                name_parts = filename.rsplit(".", 1)
                for size_name in self.image_sizes.keys():
                    variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
                    variant_blob = self.bucket.blob(
                        f"uploads/{variant_filename}")
                    if variant_blob.exists():
                        variant_blob.delete()
            else:
                # Delete from local storage
                local_file = self.local_upload_dir / filename
                if local_file.exists():
                    local_file.unlink()

                # Delete variants
                name_parts = filename.rsplit(".", 1)
                for size_name in self.image_sizes.keys():
                    variant_filename = f"{name_parts[0]}_{size_name}.{name_parts[1]}"
                    local_variant = self.local_upload_dir / variant_filename
                    if local_variant.exists():
                        local_variant.unlink()

            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Singleton instance
storage_service = StorageService()
