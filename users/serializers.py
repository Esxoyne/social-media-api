from rest_framework import serializers
from django.contrib.auth import get_user_model

from django_countries.serializers import CountryFieldMixin

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "is_staff")
        read_only_fields = ("is_staff",)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username")


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class ProfileSerializer(
    CountryFieldMixin,
    serializers.ModelSerializer,
):
    user = UserListSerializer(read_only=True)
    followers = serializers.IntegerField(
        source="follower_count",
        read_only=True,
    )
    following = serializers.IntegerField(
        source="following_count",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "picture",
            "bio",
            "gender",
            "country",
            "followers",
            "following",
        )
        read_only_fields = ("picture",)


class ProfileListSerializer(
    CountryFieldMixin,
    serializers.HyperlinkedModelSerializer,
):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = (
            "url",
            "username",
            "picture",
        )
        extra_kwargs = {
            "url": {"view_name": "users:profile-detail"},
        }


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    country = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "picture",
            "bio",
            "gender",
            "country",
        )


class ProfilePictureSerializer(serializers.ModelSerializer):
    def validate_picture(self, picture):
        if picture.size > 1000000:
            raise serializers.ValidationError(
                "Image size exceeded: 1 MB"
            )

        return picture

    class Meta:
        model = Profile
        fields = (
            "id",
            "picture",
        )


class FollowerListSerializer(serializers.ModelSerializer):
    followers = ProfileListSerializer(many=True)

    class Meta:
        model = Profile
        fields = (
            "followers",
        )


class FollowingListSerializer(serializers.ModelSerializer):
    following = ProfileListSerializer(many=True)

    class Meta:
        model = Profile
        fields = (
            "following",
        )
