# apps/accounts/views.py

from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.views import BaseAPIView
from core.exceptions import ValidationError
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Registration failed",
                errors=serializer.errors
            )

        user = serializer.save()
        return self.success_response(
            data=UserSerializer(user).data,
            message="User registered successfully",
            status_code=201
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]