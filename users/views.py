from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

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
    Retrieve, Update account info
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ManageProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve, Update user profile
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
    Retrieve, Update user profile picture
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


class ProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve user profiles
    """

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileRetrieveSerializer
    permission_classes = (AllowAny,)


class ProfileFollowView(APIView):
    """
    Follow/unfollow profile
    """

    def get_object(self, pk):
        return get_object_or_404(Profile, pk=pk)

    def post(self, request, pk, *args, **kwargs):
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
        user_profile = request.user.profile
        target = self.get_object(pk)

        if user_profile != target and user_profile in target.followers.all():
            target.followers.remove(user_profile)
            target.save()

            return Response({}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowerListView(generics.RetrieveAPIView):
    queryset = Profile.objects.prefetch_related("followers__user")
    serializer_class = FollowerListSerializer
    permission_classes = (AllowAny,)


class FollowingListView(generics.RetrieveAPIView):
    queryset = Profile.objects.prefetch_related("following__user")
    serializer_class = FollowingListSerializer
    permission_classes = (AllowAny,)
