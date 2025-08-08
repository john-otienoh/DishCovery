from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import status
from http.client import responses
from multiprocessing import context
import os
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from utils.jwt_token import token_decoder, token_generator
from django.urls import reverse
from django.core.mail import EmailMessage
from utils.email import EmailThread
from django.core.cache import cache

from .serializers import *
from .renderers import UserRenderer

User = get_user_model()


# Get the user from active model
class UserCreationView(APIView):
    """Sign Up class View"""

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = token_generator(user)
        return Response(
            {
                "token": token,
                "msg": "You registered successfuly!",
                "email_verification_required": not user.is_verified,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


class EmailVerificationAPIView(APIView):
    """Confirm users email"""

    def get(self, request, token):
        # Decode the token to get the user id
        user_id = token_decoder(token)
        # Attempt to retrieve the user and activate the account
        try:
            user = get_object_or_404(User, pk=user_id)
            if user.is_verified:
                return Response(
                    {"message": "You are already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response(
                {"message": "Account activated successfully!"},
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response(
                {"error": "Activation link is invalid!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError:
            return Response(user_id)


class ResendEmailVerificationAPIView(APIView):
    """Resend a verification email to user"""

    permission_classes = [AllowAny]
    serializer_class = ResendEmailVerificationSerializer

    def post(self, request):
        serializer = ResendEmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            # Get user from serilizer validate method
            user = serializer.validated_data["user"]
            # Generate a jwt token for resend confirm email
            token = token_generator(user)
            # Resending confirm email token
            confirm_url = self.request.build_absolute_uri(
                reverse("confirm_email", kwargs={"token": token["access"]})
            )
            msg = f"for confirm email click on: {confirm_url}"
            email_obj = EmailMessage(subject="Confirm email", body=msg, from_email=os.environ.get('EMAIL_USER'), to=[user.email])
            # Sending email with threading
            EmailThread(email_obj).start()
            return Response(
                {"message: The activation email has been sent again successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            cache_key = f'failed_login_{email}'
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, timeout=3600)
        
            if attempts >= 3:
                return Response({
                    "error": "Too many failed attempts. Try again later or reset your password.",
                    "retry_after": 3600
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)

            if user is None:
                return Response(
                    {"errors": "Login Faild , Email or Password is not valid !"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if not user.is_active:
                return Response(
                    {"error": "Account is not active"}, status=status.HTTP_403_FORBIDDEN
                )

            if not user.is_verified:
                return Response(
                    {"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN
                )
            token = token_generator(user)
            return Response(
                {"token": token, "user_id": user.id, "email": user.email},
                status=status.HTTP_200_OK,
            )


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid():
            return Response(
                {"msg": "password changed successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Reset Password's Link Sent, Please Check Your Email BOX."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = PasswordResetConfirmSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializer.is_valid():
            return Response(
                {"msg": "password reset successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token_object = RefreshToken(refresh_token)
            token_object.blacklist()
            return Response(
                {"msg": "You Logout Successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
