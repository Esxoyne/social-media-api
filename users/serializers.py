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
        fields = ("id", "username", "is_staff")
        read_only_fields = ("is_staff",)


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

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "picture",
            "bio",
            "gender",
            "country",
        )
        read_only_fields = ("picture",)


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    country = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "picture",
            "bio",
            "gender",
            "country",
        )


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "picture",
        )
