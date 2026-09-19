# backend/core/email/base.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict


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