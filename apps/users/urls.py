from django.urls import path
from apps.users.views import (
    FollowerListView,
    FollowingListView,
    FollowView,
    ProfileView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("me/", ProfileView.as_view(), name="user-me"),
    path("<str:username>/", UserDetailView.as_view(), name="user-detail"),
    path("<str:username>/follow/", FollowView.as_view(), name="user-follow"),
    path("<str:username>/followers/", FollowerListView.as_view(), name="user-followers"),
    path("<str:username>/following/", FollowingListView.as_view(), name="user-following"),
]
