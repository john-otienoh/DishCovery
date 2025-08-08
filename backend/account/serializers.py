from django.core.mail import EmailMessage
from django.urls import reverse
import os
from .models import Profile
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from utils.email import EmailThread
from utils.jwt_token import token_generator

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user registration with email verification
    """

    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, required=True
    )
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, required=True
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("id", "email", "name", "password", "confirm_password", "remember_me")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        # Password matching validation
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"error": "The passwords do not match"})

        # Password complexity validation
        try:
            validate_password(attrs["password"])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # Email uniqueness check
        email = attrs.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already registered"})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.pop("confirm_password")
        remember_me = validated_data.pop("remember_me", False)

        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            password=validated_data["password"],
        )

        # Generate and send email verification token
        token = token_generator(user)
        confirm_url = request.build_absolute_uri(
            reverse("confirm_email", kwargs={"token": token["access"]})
        )
        msg = f"Please click on the following link to confirm your email: {confirm_url}"
        email_obj = EmailMessage(subject="Confirm your email", body=msg, from_email=os.environ.get('EMAIL_USER'),to=[user.email])
        EmailThread(email_obj).start()

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Handles user authentication
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    remember_me = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ["email", "password", "remember_me"]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Handles password change for authenticated users
    """

    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    confirm_new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )

    def validate(self, attrs):
        user = self.context.get("user")

        # Verify old password
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Incorrect current password"}
            )

        # Password matching validation
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"error": "The new passwords do not match"}
            )

        # Password complexity validation
        try:
            validate_password(attrs["new_password"])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def save(self, **kwargs):
        user = self.context.get("user")
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Handles password reset requests
    """

    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email does not exist"}
            )

        # Generate password reset token and link
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"{self.context.get('request').build_absolute_uri('/')}reset-password/{uid}/{token}/"

        # Send email with reset link
        body = (
            f"Please click on the following link to reset your password: {reset_link}"
        )
        email_obj = EmailMessage(subject="Password Reset Request", body=body, from_email=os.environ.get('EMAIL_USER'), to=user.email)
        EmailThread(email_obj).start()

        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Handles password reset confirmation
    """

    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    confirm_new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )

    def validate(self, attrs):
        # Password matching validation
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"error": "The passwords do not match"})

        # Password complexity validation
        try:
            validate_password(attrs["new_password"])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        # Token and UID validation
        uid = self.context.get("uid")
        token = self.context.get("token")

        try:
            user_id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"error": "Invalid user identifier"})

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError({"error": "Invalid or expired token"})

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ResendEmailVerificationSerializer(serializers.Serializer):
    """
    Handles resending email verification.
    """

    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email does not exist"}
            )

        if user.is_verified:
            raise serializers.ValidationError({"email": "Email is already verified"})

        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """User Profile Serializer"""

    model = Profile
    fields = ["name", "bio", "gender", "avatar"]
