from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.notifications.services import create_notification
from .models import Follow
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    FollowSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserPublicSerializer,
)

User = get_user_model()


# ─── Auth views ────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/ — create a new account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserPublicSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/login/ — obtain JWT token pair."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    request=inline_serializer("LogoutRequest", fields={"refresh": serializers.CharField()}),
    responses={200: inline_serializer("LogoutResponse", fields={"detail": serializers.CharField()})},
    description="Blacklist the refresh token to invalidate the session.",
)
class LogoutView(APIView):
    """POST /api/v1/auth/logout/ — blacklist the refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."})
        except Exception:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    request="apps.users.serializers.ChangePasswordSerializer",
    responses={200: inline_serializer("ChangePasswordResponse", fields={"detail": serializers.CharField()})},
    description="Change the authenticated user's password.",
)
class ChangePasswordView(APIView):
    """POST /api/v1/auth/change-password/ — change own password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Incorrect password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated successfully."})


# ─── Profile views ─────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET / PUT / PATCH /api/v1/users/me/ — own profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """GET /api/v1/users/<username>/ — public profile of any user."""

    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"
    queryset = User.objects.all()


class UserListView(generics.ListAPIView):
    """GET /api/v1/users/ — search users by username."""

    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["username", "bio"]

    def get_queryset(self):
        return User.objects.all()


# ─── Follow views ──────────────────────────────────────────────────────────────

@extend_schema(
    request=None,
    responses={
        200: inline_serializer("UnfollowResponse", fields={"detail": serializers.CharField(), "following": serializers.BooleanField()}),
        201: inline_serializer("FollowResponse", fields={"detail": serializers.CharField(), "following": serializers.BooleanField()}),
    },
    description="Follow or unfollow a user. Toggles on repeated calls.",
)
class FollowView(APIView):
    """POST /api/v1/users/<username>/follow/ — follow or unfollow."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target,
        )

        if not created:
            # Unfollow
            follow.delete()
            User.objects.filter(pk=request.user.pk).update(
                following_count=max(0, request.user.following_count - 1)
            )
            User.objects.filter(pk=target.pk).update(
                followers_count=max(0, target.followers_count - 1)
            )
            return Response({"detail": "Unfollowed.", "following": False})

        # Follow
        User.objects.filter(pk=request.user.pk).update(
            following_count=request.user.following_count + 1
        )
        User.objects.filter(pk=target.pk).update(
            followers_count=target.followers_count + 1
        )
        create_notification(
            recipient=target,
            actor=request.user,
            verb="started following you",
            notification_type="follow",
        )
        return Response({"detail": "Followed.", "following": True}, status=status.HTTP_201_CREATED)


class FollowerListView(generics.ListAPIView):
    """GET /api/v1/users/<username>/followers/"""

    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Follow.objects.none()
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Follow.objects.filter(following=user).select_related("follower", "following")


class FollowingListView(generics.ListAPIView):
    """GET /api/v1/users/<username>/following/"""

    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Follow.objects.none()
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Follow.objects.filter(follower=user).select_related("follower", "following")