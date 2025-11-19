from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    EmailVerificationView,
    PasswordResetRequestView,
    PasswordResetValidateCodeView,
    PasswordResetConfirmView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('verify-email/', EmailVerificationView.as_view(), name='auth_verify_email'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/validate-code/', PasswordResetValidateCodeView.as_view(), name='password_reset_validate_code'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
