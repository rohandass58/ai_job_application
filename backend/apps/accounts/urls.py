# apps/accounts/urls.py

from django.urls import path
from .views import RegisterView, LoginView, RefreshView, EmailCredentialView, EmailCredentialTestView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("email-credential/", EmailCredentialView.as_view(), name="email_credential"),
    path("email-credential/test/", EmailCredentialTestView.as_view(), name="email_credential_test"),
]

