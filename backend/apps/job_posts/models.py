# apps/job_posts/models.py

from django.db import models
from django.conf import settings
from core.models import BaseModel


class JobPost(BaseModel):
    """
    A job posting extracted from a screenshot.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_posts"
    )

    # Original screenshot
    screenshot = models.ImageField(upload_to="job_screenshots/")

    # Extracted fields
    company = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=200, blank=True)
    skills = models.JSONField(default=list, blank=True)          # list of skills
    hr_email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    raw_text = models.TextField(blank=True)

    # Status of parsing
    is_parsed = models.BooleanField(default=False)
    parse_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} - {self.role}" if self.company else f"JobPost #{self.id}"