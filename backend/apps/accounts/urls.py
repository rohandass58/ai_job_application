# apps/accounts/urls.py

from django.urls import path
from .views import (
    RegisterView,
    RegisterInitView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    RefreshView,
    EmailCredentialView,
    EmailCredentialTestView,
)

urlpatterns = [
    # Legacy registration (direct - no email verification)
    path("register/", RegisterView.as_view(), name="register"),
    # New OTP-based registration flow
    path("register/init/", RegisterInitView.as_view(), name="register_init"),
    path("register/verify/", VerifyOTPView.as_view(), name="register_verify"),
    path("register/resend/", ResendOTPView.as_view(), name="register_resend"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("email-credential/", EmailCredentialView.as_view(), name="email_credential"),
    path("email-credential/test/", EmailCredentialTestView.as_view(), name="email_credential_test"),
]

