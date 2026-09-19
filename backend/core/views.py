# backend/core/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import APIResponseMixin


class BaseAPIView(APIResponseMixin, APIView):
    """
    Base API View for the entire project.
    - Already includes APIResponseMixin
    - Default permission = IsAuthenticated (can be overridden)
    """

    permission_classes = [IsAuthenticated]