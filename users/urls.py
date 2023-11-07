from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from . import views


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("me/account/", views.ManageAccountView.as_view(), name="manage-user"),
    path(
        "me/profile/",
        views.ManageProfileView.as_view(),
        name="manage-profile",
    ),
    path(
        "me/profile/upload-picture/",
        views.ManageProfilePictureView.as_view(),
        name="upload-profile-picture",
    ),
    path("profiles/", views.ProfileListView.as_view(), name="profile-list"),
    path(
        "profiles/<int:pk>/",
        views.ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "profiles/<int:pk>/follow/",
        views.ProfileFollowView.as_view(),
        name="profile-follow",
    ),
    path(
        "profiles/<int:pk>/followers/",
        views.FollowerListView.as_view(),
        name="profile-followers",
    ),
    path(
        "profiles/<int:pk>/following/",
        views.FollowingListView.as_view(),
        name="profile-following",
    ),
]

app_name = "users"
