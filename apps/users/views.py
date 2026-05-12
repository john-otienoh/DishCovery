from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, ChangePasswordSerializer, FollowSerializer,
    UserProfileSerializer, UserPublicSerializer, CustomTokenObtainPairSerializer
)
from .models import Follow
from apps.notifications.services import create_notification

# Create your views here.
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh= RefreshToken.for_user(user)
        return Response(
            {
                "user": UserPublicSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
class ChangePasswordView(APIView):
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
        user.set_password(serializer.validate_data["new_password"])
        user.save(updated_fields=["password"])
        return Response(
            {"detail": "Password updated successfully"}
        )
    
class ProfileView(generics.RetreiveUpadateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"
    queryset = User.objects.all()

class UserListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["username"]

    def def get_queryset(self):
        return User.objects.all()
        
class FollowView(APIView):
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
            following=target
        )

        if not created:
            follow.delete()
            User.objects.filter(pk=request.user.pk).update(
                following_count=max(0, request.user.following_count - 1)
            )
            User.objects.filter(pk=target.pk).update(
                followers_count=max(0, target.followers_count - 1)
            )
            return Response({"detail": "Unfollowed.", "following": False})
        
        User.objects.filter(pk=request.user.pk).update(
            following_count=request.user.following_count + 1
        )

        User.objects.filter(pk=target.pk).update(
            followers_count=max(0, target.followers_count + 1)
        )
        create_notification(
            recipient=target,
            actor=request.user,
            verb="started following you",
            notification_type="follow",
        )
        return Response({"detail": "Followed.", "following": True}, status=status.HTTP_201_CREATED)

class FollowerListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes =[permissions.AllowAny]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Follow.objects.filter(following=user).select_related("following", "follower")

class FollowingListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Follow.objects.filter(follower=user).select_related("follower", "following")