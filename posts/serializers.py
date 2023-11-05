from rest_framework import serializers

from taggit.serializers import (
    TagListSerializerField,
    TaggitSerializer,
)

from .models import Post, PostImage
from users.serializers import (
    ProfileRetrieveSerializer,
    ProfileListSerializer,
)


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image")


class PostImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("image",)


class PostSerializer(
    TaggitSerializer,
    serializers.ModelSerializer,
):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )
    tags = TagListSerializerField(
        child=serializers.CharField(allow_blank=True, allow_null=True),
    )
    likes = serializers.IntegerField(source="like_count", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "text",
            "images",
            "likes",
            "created_at",
            "updated_at",
            "tags",
        )
        read_only_fields = ("user", "likes")

    def create(self, validated_data):
        images = validated_data.pop("images", None)
        post = super().create(validated_data)
        if images:
            for image in images:
                PostImage.objects.create(post=post, image=image)
        return post


class PostListSerializer(PostSerializer):
    user = ProfileListSerializer(source="user.profile", read_only=True)
    images = PostImageListSerializer(many=True, read_only=True)


class PostRetrieveSerializer(PostSerializer):
    user = ProfileRetrieveSerializer(source="user.profile", read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
