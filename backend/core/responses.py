from rest_framework.response import Response
from rest_framework import status


class APIResponseMixin:
    """
    Mixin that provides standardized success/error responses.
    Use it in every APIView / ViewSet.
    """

    def success_response(
        self,
        data=None,
        message: str = "OK",
        status_code: int = status.HTTP_200_OK,
    ):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
                "errors": None,
            },
            status=status_code,
        )

    def error_response(
        self,
        message: str = "Error",
        errors=None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        return Response(
            {
                "success": False,
                "message": message,
                "data": None,
                "errors": errors,
            },
            status=status_code,
        )