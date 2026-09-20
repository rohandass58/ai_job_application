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
        Get SMTP configuration for a user.
        ONLY uses user's own EmailCredential - NO fallback to Brevo/global settings.
        Raises EmailSendError if user has no verified credential.
        """
        if not user:
            from core.exceptions import EmailSendError
            raise EmailSendError("User required for sending email")
        
        if not hasattr(user, 'email_credential'):
            from core.exceptions import EmailSendError
            raise EmailSendError("No email credential configured. Please add your Gmail App Password in Email Settings.")
        
        try:
            credential = user.email_credential
            if not credential or not credential.is_verified:
                from core.exceptions import EmailSendError
                raise EmailSendError("Email credential not verified. Please verify in Email Settings.")
            
            from core.crypto import decrypt
            return {
                'host': credential.smtp_host,
                'port': credential.smtp_port,
                'username': credential.email,
                'password': decrypt(credential.encrypted_password),
                'use_tls': True,
                'from_email': credential.email,
            }
        except EmailSendError:
            raise
        except Exception as e:
            from core.exceptions import EmailSendError
            raise EmailSendError(f"Failed to load email credential: {str(e)}")