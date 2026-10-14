# core/email/service.py

"""
Email sending service - single entry point for all email sending.
Wraps the factory and translates low-level exceptions to domain exceptions.
"""

from core.email.factory import get_email_sender
from core.exceptions import EmailDeliveryFailed


def send_email(
    *,
    sender=None,
    to_email: str,
    subject: str,
    body: str,
    from_name: str,
    reply_to: str | None = None,
    attachments: list | None = None,
):
    """
    Send an email using the appropriate sender.
    
    Args:
        sender: Optional pre-configured EmailSender instance.
                If not provided, will use get_email_sender() with system defaults.
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_name: Display name for sender
        reply_to: Reply-to email address
        attachments: List of attachment dicts
    
    Raises:
        EmailDeliveryFailed: If email sending fails
    """
    if sender is None:
        sender = get_email_sender("smtp")
    
    try:
        sender.send(
            to_email=to_email,
            subject=subject,
            body=body,
            from_name=from_name,
            reply_to=reply_to,
            attachments=attachments,
        )
    except Exception as e:
        # Exception translation: low-level SMTP error → domain exception
        raise EmailDeliveryFailed(f"Failed to send email: {str(e)}")
