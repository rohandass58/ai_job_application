# apps/accounts/views.py

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from core.views import BaseAPIView
from core.exceptions import ValidationError
from .serializers import RegisterSerializer, UserSerializer, EmailCredentialSerializer, EmailCredentialReadSerializer
from core.models import EmailCredential


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


class LoginView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Invalid username or password",
                errors=serializer.errors,
                status_code=401,
            )

        return self.success_response(
            data=serializer.validated_data,
            message="Login successful",
        )
    

class RefreshView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Session expired. Please login again.",
                errors=serializer.errors,
                status_code=401,
            )

        return self.success_response(
            data=serializer.validated_data,
            message="Token refreshed",
        )


class EmailCredentialView(BaseAPIView):
    """Manage user's own SMTP credentials (Gmail App Password)"""
    
    def get(self, request):
        """Get current email credential (if any)"""
        try:
            credential = request.user.email_credential
            serializer = EmailCredentialReadSerializer(credential)
            return self.success_response(data=serializer.data)
        except EmailCredential.DoesNotExist:
            return self.success_response(data=None, message="No email credential configured")

    def post(self, request):
        """Create or update email credential"""
        try:
            credential = request.user.email_credential
            serializer = EmailCredentialSerializer(credential, data=request.data, partial=True, context={"request": request})
        except EmailCredential.DoesNotExist:
            serializer = EmailCredentialSerializer(data=request.data, context={"request": request})
        
        if not serializer.is_valid():
            raise ValidationError(message="Invalid data", errors=serializer.errors)
        
        serializer.save()
        return self.success_response(
            data=EmailCredentialReadSerializer(serializer.instance).data,
            message="Email credential saved successfully"
        )

    def patch(self, request):
        """Update email credential (partial update)"""
        return self.post(request)

    def delete(self, request):
        """Delete email credential"""
        try:
            credential = request.user.email_credential
            credential.delete()
            return self.success_response(message="Email credential deleted")
        except EmailCredential.DoesNotExist:
            raise ValidationError(message="No email credential to delete", status_code=404)


class EmailCredentialTestView(BaseAPIView):
    """Test email credential by sending a test email"""
    
    def post(self, request):
        try:
            credential = request.user.email_credential
        except EmailCredential.DoesNotExist:
            raise ValidationError(message="No email credential configured", status_code=404)
        
        test_email = request.data.get("test_email")
        if not test_email:
            raise ValidationError(message="test_email is required")
        
        try:
            from core.email.factory import get_email_sender
            sender = get_email_sender(user=request.user)
            from_name = request.user.get_full_name() or request.user.username
            
            sender.send(
                to_email=test_email,
                subject="Test Email from JobApply",
                body=f"Hi {from_name},\n\nThis is a test email from your JobApply account.\nYour Gmail App Password is working correctly!\n\nBest regards,\nJobApply Team",
                from_name=from_name,
                reply_to=request.user.email,
            )
            # Mark as verified on successful test send
            credential.is_verified = True
            credential.save(update_fields=["is_verified"])
            return self.success_response(message="Test email sent successfully")
        except Exception as e:
            raise ValidationError(message=f"Failed to send test email: {str(e)}")