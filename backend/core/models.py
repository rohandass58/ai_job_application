# backend/core/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets

from core.exceptions import (
    OTPAlreadyUsed,
    OTPExpired,
    OTPInvalid,
    OTPMaxAttemptsExceeded,
)


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


class EmailOTP(BaseModel):
    """
    One-Time Password for email verification during registration.
    """

    email = models.EmailField(db_index=True)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ("register", "Registration"),
            ("password_reset", "Password Reset"),
        ],
        default="register",
    )
    expires_at = models.DateTimeField()
    last_sent_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)

    # Store registration data temporarily
    reg_username = models.CharField(max_length=150, blank=True, default="")
    reg_password_hash = models.CharField(max_length=128, blank=True, default="")
    reg_first_name = models.CharField(max_length=150, blank=True, default="")
    reg_last_name = models.CharField(max_length=150, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["email", "purpose", "is_used"]),
        ]

    def __str__(self):
        return f"OTP for {self.email} ({self.purpose})"

    @classmethod
    def generate_otp(cls):
        """Generate a 6-digit OTP."""
        return f"{secrets.randbelow(1000000):06d}"

    def is_valid(self):
        """Check if OTP is still valid."""
        return not self.is_used and self.attempts < self.max_attempts and timezone.now() < self.expires_at

    def get_invalid_reason(self):
        """Return specific reason why OTP is invalid, or None if valid."""
        if self.is_used:
            return "used"
        if self.attempts >= self.max_attempts:
            return "max_attempts"
        if timezone.now() >= self.expires_at:
            return "expired"
        return None

    def ensure_valid(self, otp_code):
        """Validate OTP code, incrementing attempts on failure. Raises domain exceptions."""
        if self.is_used:
            raise OTPAlreadyUsed()
        if self.attempts >= self.max_attempts:
            raise OTPMaxAttemptsExceeded()
        if timezone.now() >= self.expires_at:
            raise OTPExpired()
        if self.otp_code != otp_code:
            self.increment_attempts()
            raise OTPInvalid()

    def increment_attempts(self):
        """Increment attempt counter."""
        self.attempts += 1
        self.save(update_fields=["attempts"])

    def mark_used(self):
        """Mark OTP as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])