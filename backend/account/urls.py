from django.urls import path, include
from .views import *

urlpatterns = [
    path("register/", UserCreationView.as_view(), name="register"),
    path(
        "confirm_email/<str:token>/",
        EmailVerificationAPIView.as_view(),
        name="confirm_email",
    ),
    path(
        "resend_confirm_email/",
        ResendEmailVerificationAPIView.as_view(),
        name="resend_confirm_email",
    ), 
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("change_password/", UserChangePasswordView.as_view(), name="change_password"),
    path("reset-password/", ResetPasswordRequestView.as_view(), name="reset-password"),
    path(
        "reset-password/<uid>/<token>/",
        ResetPasswordView.as_view(),
        name="reset-password-done",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
