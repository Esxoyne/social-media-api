from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile

from .serializers import (
    ProfilePictureSerializer,
    ProfileRetrieveSerializer,
    ProfileSerializer,
    UserSerializer,
    UserSignUpSerializer,
)


class UserSignUpView(generics.GenericAPIView):
    """
    Endpoint for creating a new user.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserSignUpSerializer

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {
            "refresh": str(token),
            "access": str(token.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update user info.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ManageProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve, Update user profile.
    """

    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return ProfileRetrieveSerializer

        return ProfileSerializer


class ManageProfilePictureView(generics.RetrieveUpdateAPIView):
    """
    Retrieve, Update user profile picture.
    """

    serializer_class = ProfilePictureSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class ProfileListView(generics.ListAPIView):
    """
    List user profiles.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = self.queryset.all()

        if self.request.method.lower() == "get":
            queryset = queryset.select_related("user")

        username = self.request.query_params.get("username")
        bio = self.request.query_params.get("bio")
        country = self.request.query_params.get("country")

        if username:
            queryset = queryset.filter(user__username__icontains=username)

        if bio:
            queryset = queryset.filter(bio__icontains=bio)

        if country:
            queryset = queryset.filter(country__icontains=country)

        return queryset

class ProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve user profiles.
    """

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileRetrieveSerializer
    permission_classes = (AllowAny,)
