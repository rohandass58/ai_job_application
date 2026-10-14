# apps/accounts/views.py

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from django.contrib.auth import get_user_model
from core.views import BaseAPIView
from core.exceptions import (
    ValidationError,
    AuthenticationFailed,
    TokenExpired,
)
from .serializers import (
    RegisterSerializer,
    RegisterInitSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    UserSerializer,
    EmailCredentialSerializer,
    EmailCredentialReadSerializer,
)
from .services import AccountService, EmailCredentialService


User = get_user_model()


class RegisterView(BaseAPIView):
    """
    Legacy registration endpoint - kept for backward compatibility.
    New registration should use RegisterInitView -> VerifyOTPView flow.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Registration failed",
                errors=serializer.errors
            )

        user = AccountService.register_user(**serializer.validated_data)
        return self.success_response(
            data=UserSerializer(user).data,
            message="User registered successfully",
            status_code=201
        )


class RegisterInitView(BaseAPIView):
    """
    Step 1: Initiate registration by sending OTP to email.
    Does NOT create user yet - only sends verification code.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterInitSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Registration failed",
                errors=serializer.errors
            )

        # data = AccountService.initiate_registration(**serializer.validated_data)
        data = AccountService.initiate_registration(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        return self.success_response(
            data=data,
            message="Verification code sent to your email. Please check your inbox."
        )


class VerifyOTPView(BaseAPIView):
    """
    Step 2: Verify OTP and create the user account.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Verification failed",
                errors=serializer.errors
            )

        user = AccountService.verify_otp_and_create_user(
            email=serializer.validated_data["email"],
            otp_code=serializer.validated_data["otp_code"],
        )

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)


        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return self.success_response(
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            message="Email verified! Account created successfully.",
            status_code=201
        )


class ResendOTPView(BaseAPIView):
    """
    Resend OTP for registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Resend failed",
                errors=serializer.errors
            )

        data = AccountService.resend_otp(serializer.validated_data["email"])
        return self.success_response(
            data=data,
            message="New verification code sent to your email."
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LoginView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()

        # Delegate to service - it raises domain exceptions
        data = AccountService.authenticate_user(
            username=username,
            password=request.data.get("password", "")
        )

        return self.success_response(
            data=data,
            message="Login successful",
        )


class RefreshView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise ValidationError("Refresh token is required")

        data = AccountService.refresh_token(refresh_token)
        return self.success_response(
            data=data,
            message="Token refreshed",
        )


class EmailCredentialView(BaseAPIView):
    """Manage user's own SMTP credentials (Gmail App Password)"""

    def get(self, request):
        """Get current email credential (if any)"""
        credential = EmailCredentialService.get_credential(request.user)
        if credential:
            serializer = EmailCredentialReadSerializer(credential)
            return self.success_response(data=serializer.data)
        return self.success_response(data=None, message="No email credential configured")

    def post(self, request):
        """Create or update email credential"""
        serializer = EmailCredentialSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            raise ValidationError(message="Invalid data", errors=serializer.errors)

        credential = EmailCredentialService.save_credential(
            user=request.user,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            smtp_host=serializer.validated_data.get("smtp_host", "smtp.gmail.com"),
            smtp_port=serializer.validated_data.get("smtp_port", 587),
        )
        return self.success_response(
            data=EmailCredentialReadSerializer(credential).data,
            message="Email credential saved successfully"
        )

    def patch(self, request):
        """Update email credential (partial update)"""
        return self.post(request)

    def delete(self, request):
        """Delete email credential"""
        EmailCredentialService.delete_credential(request.user)
        return self.success_response(message="Email credential deleted")


class EmailCredentialTestView(BaseAPIView):
    """Test email credential by sending a test email"""

    def post(self, request):
        test_email = request.data.get("test_email")
        if not test_email:
            raise ValidationError(message="test_email is required")

        EmailCredentialService.test_and_verify_credential(request.user, test_email)
        return self.success_response(message="Test email sent successfully")
