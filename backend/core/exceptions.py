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


# Concrete exceptions
class AIProviderError(AppException):
    """Raised when Gemini / Groq fails"""
    pass


class EmailSendError(AppException):
    """Raised when email sending fails"""
    pass


class ParsingError(AppException):
    """Raised when job screenshot parsing fails"""
    pass


class ValidationError(AppException):
    """Raised for business-level validation errors"""
    pass


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
        response.data = {
            "success": False,
            "message": "Something went wrong",
            "data": None,
            "errors": response.data,
        }

    return response