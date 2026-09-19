# apps/resumes/models.py

from django.db import models
from django.conf import settings
from core.models import BaseModel


class Resume(BaseModel):
    """
    Master resume of a student.
    One user can have multiple resumes (optional), but usually one active.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes"
    )
    title = models.CharField(max_length=150, default="My Resume")
    file = models.FileField(upload_to="resumes/")
    is_primary = models.BooleanField(default=True)

    # Optional: extracted text for AI later
    extracted_text = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.title}"