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
    path("sign-out/", TokenBlacklistView.as_view(), name="sign_out"),
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
]

app_name = "users"
