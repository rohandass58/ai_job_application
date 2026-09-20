# backend/core/validators.py

import os
from django.core.exceptions import ValidationError as DjangoValidationError

MAX_RESUME_SIZE_MB = 5
MAX_IMAGE_SIZE_MB = 5

ALLOWED_RESUME_EXTENSIONS = {".pdf"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

PDF_MAGIC = b"%PDF"


def validate_resume_file(file):
    """
    Checks extension, size and the real file signature (magic bytes).
    Extension alone is not enough: anyone can rename malware.exe -> cv.pdf.
    """
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise DjangoValidationError("Only PDF resumes are allowed.")

    if file.size > MAX_RESUME_SIZE_MB * 1024 * 1024:
        raise DjangoValidationError(f"Resume must be under {MAX_RESUME_SIZE_MB} MB.")

    header = file.read(4)
    file.seek(0)
    if header != PDF_MAGIC:
        raise DjangoValidationError("File is not a valid PDF.")


def validate_image_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise DjangoValidationError("Only JPG, PNG or WEBP images are allowed.")

    if file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise DjangoValidationError(f"Image must be under {MAX_IMAGE_SIZE_MB} MB.")