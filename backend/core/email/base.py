# backend/core/email/base.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from django.conf import settings


class EmailSender(ABC):
    """
    Abstract interface for email sending.
    Later we can have SMTP, Brevo, SendGrid, etc. implementations.
    """

    @abstractmethod
    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> bool:
        """
        Send an email.

        Parameters:
            to_email     → recipient email
            subject      → email subject
            body         → email body (plain text or HTML)
            from_name    → display name (e.g. "Rahul via JobApply")
            reply_to     → student's email (so HR replies go to student)
            attachments  → list of dicts: [{"filename": "...", "content": bytes, "mimetype": "..."}]

        Returns:
            True if sent successfully, otherwise raise EmailSendError
        """
        pass

    
    def _get_smtp_config(self, user=None):
        """
        Use application SMTP settings when no user is provided.
        Use verified user-specific credentials when a user is provided.
        """
        if user is None:
            from decouple import config

            return {
                "host": config("EMAIL_HOST"),
                "port": config("EMAIL_PORT", default=587, cast=int),
                "username": config("EMAIL_HOST_USER"),
                "password": config("EMAIL_HOST_PASSWORD"),
                "use_tls": config("EMAIL_USE_TLS", default=True, cast=bool),
                "from_email": config("DEFAULT_FROM_EMAIL", default=config("EMAIL_HOST_USER")),
            }

        if not hasattr(user, "email_credential"):
            from core.exceptions import EmailSendError
            raise EmailSendError(
                "No email credential configured. Please add your Gmail App Password in Email Settings."
            )

        try:
            credential = user.email_credential

            if not credential or not credential.is_verified:
                from core.exceptions import EmailSendError
                raise EmailSendError(
                    "Email credential not verified. Please verify in Email Settings."
                )

            from core.crypto import decrypt

            return {
                "host": credential.smtp_host,
                "port": credential.smtp_port,
                "username": credential.email,
                "password": decrypt(credential.encrypted_password),
                "use_tls": True,
                "from_email": credential.email,
            }

        except Exception as e:
            from core.exceptions import EmailSendError

            if isinstance(e, EmailSendError):
                raise

            raise EmailSendError(f"Failed to load email credential: {str(e)}")
