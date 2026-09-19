# backend/core/email/factory.py

from django.conf import settings
from .base import EmailSender
from .smtp import SMTPEmailSender


def get_email_sender(provider_name: str | None = None) -> EmailSender:
    """
    Factory to get the correct email sender.
    Currently only SMTP is supported.
    Later we can add Brevo, SendGrid, etc.
    """
    name = (provider_name or getattr(settings, "DEFAULT_EMAIL_PROVIDER", "smtp")).lower()

    if name == "smtp":
        return SMTPEmailSender()
    else:
        raise ValueError(f"Unknown email provider: {name}")