from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/v1/notifications/
        ?unread=true  — filter to unread only
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        qs = Notification.objects.filter(recipient=self.request.user).select_related("actor")
        if self.request.query_params.get("unread") == "true":
            qs = qs.filter(is_read=False)
        return qs


@extend_schema(
    request=inline_serializer("MarkReadRequest", fields={"ids": serializers.ListField(child=serializers.IntegerField(), required=False)}),
    responses={200: inline_serializer("MarkReadResponse", fields={"detail": serializers.CharField()})},
    description="Mark notifications as read. Pass {'ids': [...]} to target specific ones, or an empty body to mark all.",
)
class NotificationMarkReadView(APIView):
    """
    POST /api/v1/notifications/mark-read/
        body: {"ids": [1, 2, 3]}   — mark specific notifications as read
        body: {}                   — mark ALL as read
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        qs = Notification.objects.filter(recipient=request.user, is_read=False)
        ids = request.data.get("ids")
        if ids:
            qs = qs.filter(pk__in=ids)
        updated = qs.update(is_read=True)
        return Response({"detail": f"{updated} notification(s) marked as read."})


class NotificationDetailView(generics.RetrieveDestroyAPIView):
    """GET / DELETE /api/v1/notifications/<id>/"""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@extend_schema(
    responses={200: inline_serializer("UnreadCountResponse", fields={"unread_count": serializers.IntegerField()})},
    description="Return the number of unread notifications for the authenticated user.",
)
class UnreadCountView(APIView):
    """GET /api/v1/notifications/unread-count/ — quick badge count."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread_count": count})