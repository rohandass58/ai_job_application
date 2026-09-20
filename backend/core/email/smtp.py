# backend/core/email/smtp.py

from typing import List, Optional, Dict
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from .base import EmailSender
from core.exceptions import EmailSendError


class SMTPEmailSender(EmailSender):
    """
    Concrete implementation using Django's EmailMessage (SMTP).
    Works with Gmail App Password, Brevo SMTP, etc.
    """

    def __init__(self, user=None):
        self.user = user

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> bool:
        try:
            # Get SMTP config based on user credentials
            smtp_config = self._get_smtp_config(self.user)

            # Create email connection with user-specific credentials
            connection = get_connection(
                host=smtp_config['host'],
                port=smtp_config['port'],
                username=smtp_config['username'],
                password=smtp_config['password'],
                use_tls=smtp_config['use_tls'],
            )

            from_email = f"{from_name} <{smtp_config.get('from_email', smtp_config['username'])}>"

            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[to_email],
                reply_to=[reply_to] if reply_to else None,
                connection=connection,
            )

            # Attach files if any
            if attachments:
                for att in attachments:
                    email.attach(
                        filename=att["filename"],
                        content=att["content"],
                        mimetype=att.get("mimetype", "application/octet-stream"),
                    )

            email.send(fail_silently=False)
            return True

        except Exception as e:
            raise EmailSendError(f"Failed to send email: {str(e)}")