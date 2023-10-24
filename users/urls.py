from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from . import views


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("sign-up/", views.UserSignUpView.as_view(), name="sign_up"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("me/", views.ManageUserView.as_view(), name="manage_user"),
    path(
        "me/profile/",
        views.ManageProfileView.as_view(),
        name="manage_profile"
    ),
    path(
        "me/profile/upload-picture/",
        views.ManageProfilePictureView.as_view(),
        name="upload-profile-picture",
    ),
    path("profiles/", views.ProfileListView.as_view(), name="profile_list"),
    path(
        "profiles/<int:pk>/",
        views.ProfileDetailView.as_view(),
        name="profile_detail"
    ),
    path(
        "profiles/<int:pk>/follow/",
        views.ProfileFollowView.as_view(),
        name="profile_follow",
    ),
    path(
        "profiles/<int:pk>/followers/",
        views.FollowerListView.as_view(),
        name="profile_followers",
    ),
    path(
        "profiles/<int:pk>/following/",
        views.FollowingListView.as_view(),
        name="profile_following",
    ),
]

app_name = "users"
