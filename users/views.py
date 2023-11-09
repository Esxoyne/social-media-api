from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from .models import Profile
from .serializers import (
    FollowerListSerializer,
    FollowingListSerializer,
    ProfileListSerializer,
    ProfilePictureSerializer,
    ProfileRetrieveSerializer,
    ProfileSerializer,
    UserSerializer,
    UserSignUpSerializer,
)


class SignUpView(generics.GenericAPIView):
    """
    Create a new account
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


class ManageAccountView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete current user's account
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ManageProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update current user's profile
    """

    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return ProfileRetrieveSerializer

        return ProfileSerializer


class ManageProfilePictureView(generics.UpdateAPIView):
    """
    Update current user's profile picture
    """

    serializer_class = ProfilePictureSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class ProfileListView(generics.ListAPIView):
    """
    List user profiles
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=str,
                description="Search by username",
            ),
            OpenApiParameter(
                "bio",
                type=str,
                description="Search by profile bio",
            ),
            OpenApiParameter(
                "country",
                type=str,
                description="Filter by country name",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve user profile
    """

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileRetrieveSerializer
    permission_classes = (AllowAny,)


class ProfileFollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(Profile, pk=pk)

    def post(self, request, pk, *args, **kwargs):
        """
        Follow profile
        """
        user_profile = request.user.profile
        target = self.get_object(pk)

        if (
            user_profile != target
            and user_profile not in target.followers.all()
        ):
            target.followers.add(user_profile)
            target.save()

            return Response({}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, *args, **kwargs):
        """
        Unfollow profile
        """
        user_profile = request.user.profile
        target = self.get_object(pk)

        if user_profile != target and user_profile in target.followers.all():
            target.followers.remove(user_profile)
            target.save()

            return Response({}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowerListView(generics.RetrieveAPIView):
    """
    List user's followers
    """
    queryset = Profile.objects.prefetch_related("followers__user")
    serializer_class = FollowerListSerializer
    permission_classes = (AllowAny,)


class FollowingListView(generics.RetrieveAPIView):
    """
    List user's following
    """
    queryset = Profile.objects.prefetch_related("following__user")
    serializer_class = FollowingListSerializer
    permission_classes = (AllowAny,)
