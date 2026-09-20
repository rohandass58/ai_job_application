# backend/core/email/factory.py

from django.conf import settings
from django.contrib.auth import get_user_model
from .base import EmailSender
from .smtp import SMTPEmailSender

User = get_user_model()


def get_email_sender(provider_name: str | None = None, user=None) -> EmailSender:
    """
    Factory to get the correct email sender.
    Currently only SMTP is supported.
    Later we can add Brevo, SendGrid, etc.
    
    Can be called as:
    - get_email_sender()  -> uses default provider
    - get_email_sender("smtp")  -> explicit provider
    - get_email_sender(user=request.user)  -> user as keyword arg
    - get_email_sender(request.user)  -> user as positional arg (backwards compat)
    """
    # Handle case where user is passed as first positional argument
    if isinstance(provider_name, User):
        user = provider_name
        provider_name = None
    
    name = (provider_name or getattr(settings, "DEFAULT_EMAIL_PROVIDER", "smtp")).lower()

    if name == "smtp":
        return SMTPEmailSender(user=user)
    else:
        raise ValueError(f"Unknown email provider: {name}")