from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserPublicSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "actor", "verb", "notification_type", "target_id", "is_read", "created_at")
        read_only_fields = ("id", "actor", "verb", "notification_type", "target_id", "created_at")