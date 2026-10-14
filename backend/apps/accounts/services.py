# apps/accounts/services.py

"""
Business logic for accounts.
Views stay thin; error handling is centralized:
  - third-party errors are translated once, in wrappers (core.email.service.send_email)
  - "not found" cases use .first() / update_or_create, not try/except
  - IntegrityError is mapped to a domain exception in the global exception handler
"""

from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from core.crypto import decrypt, encrypt
from core.email.factory import get_email_sender
from core.email.service import send_email
from core.exceptions import (
    AuthenticationFailed,
    EmailCredentialNotFound,
    EmailCredentialNotVerified,
    OTPAlreadyUsed,
    OTPMaxAttemptsExceeded,
    OTPNotFound,
    OTPResendTooSoon,
    TokenExpired,
    UserAlreadyExists,
    ValidationError,
)
from core.models import EmailCredential, EmailOTP
from .serializers import UserSerializer

User = get_user_model()

OTP_TTL = timedelta(minutes=10)
OTP_RESEND_COOLDOWN = timedelta(seconds=60)
REGISTER = "register"
FROM_NAME = "JobApply"
NO_REPLY = "noreply@jobapply.com"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _ensure_unique(username, email):
    if User.objects.filter(username__iexact=username).exists():
        raise UserAlreadyExists(errors={"username": ["This username is already taken."]})
    if User.objects.filter(email__iexact=email).exists():
        raise UserAlreadyExists(errors={"email": ["This email is already registered."]})


def _get_active_otp(email):
    otp = (
        EmailOTP.objects
        .filter(email=email, purpose=REGISTER, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        raise OTPNotFound()
    return otp


def _send_otp_email(otp, *, subject, intro):
    send_email(
        to_email=otp.email,
        subject=subject,
        body=(
            f"Hi {otp.reg_username},\n\n"
            f"{intro}\n\n"
            f"Your verification code: {otp.otp_code}\n\n"
            f"This code will expire in {int(OTP_TTL.total_seconds() // 60)} minutes.\n\n"
            f"If you didn't request this, please ignore this email.\n\n"
            f"Best regards,\nJobApply Team"
        ),
        from_name=FROM_NAME,
        reply_to=NO_REPLY,
    )


def _get_credential_or_raise(user):
    credential = EmailCredential.objects.filter(user=user).first()
    if credential is None:
        raise EmailCredentialNotFound()
    return credential


# --------------------------------------------------------------------------- #
# Accounts
# --------------------------------------------------------------------------- #

class AccountService:

    @staticmethod
    def initiate_registration(username, email, password, first_name="", last_name=""):
        """Step 1: create OTP and send verification email. Does NOT create the user."""
        email = email.lower()
        _ensure_unique(username, email)

        with transaction.atomic():
            EmailOTP.objects.filter(
                email=email, purpose=REGISTER, is_used=False
            ).update(is_used=True)

            otp = EmailOTP.objects.create(
                email=email,
                purpose=REGISTER,
                otp_code=EmailOTP.generate_otp(),
                expires_at=timezone.now() + OTP_TTL,
                last_sent_at=timezone.now(),
                reg_username=username,
                reg_password_hash=make_password(password),  # never store raw password
                reg_first_name=first_name,
                reg_last_name=last_name,
            )

        # Outside the transaction: if sending fails, global handler returns 502
        # and the OTP simply expires unused.
        _send_otp_email(
            otp,
            subject="Verify your email - JobApply",
            intro="Welcome to JobApply! Please verify your email address using the code below.",
        )
        return {"email": email, "expires_in": int(OTP_TTL.total_seconds())}

    @staticmethod
    def verify_otp_and_create_user(email, otp_code):
        """Step 2: verify OTP and create the user account."""
        otp = _get_active_otp(email.lower())

        # Outside atomic on purpose: the attempts increment inside ensure_valid()
        # must persist even though we raise afterwards.
        otp.ensure_valid(otp_code)

        with transaction.atomic():
            locked = EmailOTP.objects.select_for_update().get(pk=otp.pk)
            if locked.is_used:  # lost a race with a concurrent request
                raise OTPAlreadyUsed()

            user = User(
                username=locked.reg_username,
                email=locked.email,
                first_name=locked.reg_first_name,
                last_name=locked.reg_last_name,
            )
            user.password = locked.reg_password_hash  # already hashed, don't re-hash
            user.save()
            locked.mark_used()

        return user

    @staticmethod
    def resend_otp(email):
        """Issue a new code for a pending registration."""
        otp = _get_active_otp(email.lower())

        if otp.attempts >= otp.max_attempts:
            # Don't reset attempts on resend (that allows infinite guessing).
            # User must restart registration instead.
            raise OTPMaxAttemptsExceeded()
        if timezone.now() < otp.last_sent_at + OTP_RESEND_COOLDOWN:
            raise OTPResendTooSoon()

        otp.otp_code = EmailOTP.generate_otp()
        otp.expires_at = timezone.now() + OTP_TTL
        otp.last_sent_at = timezone.now()
        otp.save(update_fields=["otp_code", "expires_at", "last_sent_at"])

        _send_otp_email(
            otp,
            subject="Verify your email - JobApply (New Code)",
            intro="Here's your new verification code.",
        )
        return {"email": otp.email, "expires_in": int(OTP_TTL.total_seconds())}

    @staticmethod
    def authenticate_user(username, password):
        """Single generic failure for unknown user / wrong password / inactive user."""
        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed()  # message: "Invalid credentials"

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }

    @staticmethod
    def refresh_token(refresh_token_str):
        # The one legitimate try/except: translating a third-party exception.
        try:
            serializer = TokenRefreshSerializer(data={"refresh": refresh_token_str})
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise TokenExpired()
        return serializer.validated_data


# --------------------------------------------------------------------------- #
# Email credentials
# --------------------------------------------------------------------------- #

class EmailCredentialService:

    @staticmethod
    def get_credential(user):
        return EmailCredential.objects.filter(user=user).first()

    @staticmethod
    def save_credential(user, email, password, smtp_host="smtp.gmail.com", smtp_port=587):
        credential, _ = EmailCredential.objects.update_or_create(
            user=user,
            defaults={
                "email": email,
                "smtp_host": smtp_host,
                "smtp_port": smtp_port,
                "encrypted_password": encrypt(password),
            },
        )
        return credential

    @staticmethod
    def delete_credential(user):
        deleted, _ = EmailCredential.objects.filter(user=user).delete()
        if not deleted:
            raise EmailCredentialNotFound()

    @staticmethod
    def test_and_verify_credential(user, test_email):
        if not test_email:
            raise ValidationError("test_email is required")

        credential = _get_credential_or_raise(user)
        from_name = user.get_full_name() or user.username

        send_email(
            sender=get_email_sender(user=user),
            to_email=test_email,
            subject="Test Email from JobApply",
            body=(
                f"Hi {from_name},\n\n"
                f"This is a test email from your JobApply account.\n"
                f"Your Gmail App Password is working correctly!\n\n"
                f"Best regards,\nJobApply Team"
            ),
            from_name=from_name,
            reply_to=user.email,
        )

        credential.is_verified = True
        credential.save(update_fields=["is_verified"])
        return True

    @staticmethod
    def get_smtp_config(user):
        """SMTP config for other services. decrypt() raises its own domain error."""
        credential = _get_credential_or_raise(user)
        if not credential.is_verified:
            raise EmailCredentialNotVerified()

        return {
            "host": credential.smtp_host,
            "port": credential.smtp_port,
            "username": credential.email,
            "password": decrypt(credential.encrypted_password),
            "use_tls": True,
            "from_email": credential.email,
        }
