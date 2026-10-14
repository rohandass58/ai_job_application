from abc import ABC
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class AppException(Exception, ABC):
    """
    Abstract base exception for the whole project.
    All custom exceptions must inherit from this.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors=None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors
        super().__init__(message)


# ============================================================
# DOMAIN EXCEPTIONS (Business-meaningful, not technical)
# ============================================================

# Authentication / Authorization
class AuthenticationFailed(AppException):
    """Invalid credentials provided"""
    def __init__(self, message="Invalid username or password", errors=None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, errors)


class TokenExpired(AppException):
    """JWT token has expired"""
    def __init__(self, message="Session expired. Please login again.", errors=None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, errors)


class UserNotFound(AppException):
    """User does not exist"""
    def __init__(self, message="User not found", errors=None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


class UserAlreadyExists(AppException):
    """Username or email already registered"""
    def __init__(self, message="User already exists", errors=None):
        super().__init__(message, status.HTTP_409_CONFLICT, errors)


# OTP / Verification
class OTPExpired(AppException):
    """OTP code has expired"""
    def __init__(self, message="OTP has expired. Please request a new one.", errors=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class OTPMaxAttemptsExceeded(AppException):
    """Too many failed OTP attempts"""
    def __init__(self, message="Too many failed attempts. Please request a new OTP.", errors=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class OTPAlreadyUsed(AppException):
    """OTP was already used"""
    def __init__(self, message="This OTP has already been used.", errors=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class OTPInvalid(AppException):
    """Invalid OTP code"""
    def __init__(self, message="Invalid OTP. Please try again.", errors=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class OTPNotFound(AppException):
    """No OTP found for email"""
    def __init__(self, message="No verification code found. Please request a new one.", errors=None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


class OTPResendTooSoon(AppException):
    """OTP resend requested too soon"""
    def __init__(self, message="Please wait before requesting a new code.", errors=None):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, errors)


# Email
class EmailDeliveryFailed(AppException):
    """Failed to send email (wraps SMTP errors)"""
    def __init__(self, message="Failed to send email", errors=None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, errors)


class EmailCredentialNotVerified(AppException):
    """Email credential exists but not verified"""
    def __init__(self, message="Email credential not verified. Please verify in Email Settings.", errors=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class EmailCredentialNotFound(AppException):
    """No email credential configured"""
    def __init__(self, message="No email credential configured. Please add your Gmail App Password.", errors=None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


# AI / External Services
class AIProviderError(AppException):
    """Raised when Gemini / Groq fails"""
    def __init__(self, message="AI service temporarily unavailable", errors=None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, errors)


class ParsingError(AppException):
    """Raised when job screenshot parsing fails"""
    def __init__(self, message="Failed to parse job post", errors=None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, errors)


# Generic Business Validation
class ValidationError(AppException):
    """Raised for business-level validation errors"""
    pass


class NotFound(AppException):
    """Generic not found"""
    def __init__(self, message="Resource not found", errors=None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


class Conflict(AppException):
    """Generic conflict (duplicate)"""
    def __init__(self, message="Resource already exists", errors=None):
        super().__init__(message, status.HTTP_409_CONFLICT, errors)


# ============================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================

# Old name -> New domain exception
EmailSendError = EmailDeliveryFailed

__all__ = [
    "AppException",
    # Auth
    "AuthenticationFailed",
    "TokenExpired",
    "UserNotFound",
    "UserAlreadyExists",
    # OTP
    "OTPExpired",
    "OTPMaxAttemptsExceeded",
    "OTPAlreadyUsed",
    "OTPInvalid",
    "OTPNotFound",
    "OTPResendTooSoon",
    # Email
    "EmailDeliveryFailed",
    "EmailSendError",  # alias
    "EmailCredentialNotVerified",
    "EmailCredentialNotFound",
    # AI
    "AIProviderError",
    "ParsingError",
    # Generic
    "ValidationError",
    "NotFound",
    "Conflict",
    # Handler
    "custom_exception_handler",
]


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

def custom_exception_handler(exc, context):
    """
    Global exception handler.
    Converts AppException → standardized JSON response.
    """
    if isinstance(exc, AppException):
        return Response(
            {
                "success": False,
                "message": exc.message,
                "data": None,
                "errors": exc.errors,
            },
            status=exc.status_code,
        )

    # Fallback to DRF's default handler
    response = exception_handler(exc, context)

    if response is not None:
        # Normalize DRF validation errors
        errors = response.data
        if isinstance(errors, dict) and "detail" in errors:
            errors = errors["detail"]
        
        response.data = {
            "success": False,
            "message": "Something went wrong",
            "data": None,
            "errors": errors,
        }

    return response