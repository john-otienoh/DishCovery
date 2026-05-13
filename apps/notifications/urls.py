from django.urls import path

from .views import (
    NotificationDetailView,
    NotificationListView,
    NotificationMarkReadView,
    UnreadCountView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("mark-read/", NotificationMarkReadView.as_view(), name="notification-mark-read"),
    path("unread-count/", UnreadCountView.as_view(), name="notification-unread-count"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
]
