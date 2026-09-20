# backend/core/models.py

from django.db import models
from django.conf import settings

class BaseModel(models.Model):
    """
    Abstract base model.
    All models in the project must inherit from this.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EmailCredential(BaseModel):
    """
    A user's own SMTP login (Gmail + App Password).
    The password is stored encrypted, never in plain text.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_credential",
    )
    email = models.EmailField()
    encrypted_password = models.TextField()
    smtp_host = models.CharField(max_length=200, default="smtp.gmail.com")
    smtp_port = models.PositiveIntegerField(default=587)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_id} <{self.email}>"