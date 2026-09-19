# apps/applications/models.py

from django.db import models
from django.conf import settings
from core.models import BaseModel


class Application(BaseModel):
    """
    Represents one job application attempt.
    """

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("ready", "Ready to Send"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    job_post = models.ForeignKey(
        "job_posts.JobPost",
        on_delete=models.CASCADE,
        related_name="applications"
    )
    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications"
    )

    # Generated email
    subject = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)

    # Final recipient (usually extracted HR email)
    to_email = models.EmailField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )
    error_message = models.TextField(blank=True)

    # When it was actually sent
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} → {self.job_post.company} ({self.status})"