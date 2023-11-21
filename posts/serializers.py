from rest_framework import serializers

from taggit.serializers import (
    TagListSerializerField,
    TaggitSerializer,
)

from .models import Post, PostImage
from users.serializers import (
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

    def validate_images(self, images):
        if len(images) > 10:
            raise serializers.ValidationError(
                "Cannot upload more than 10 images to a post"
            )

        for image in images:
            if image.size > 5000000:
                raise serializers.ValidationError(
                    "Max image size exceeded: 5 MB"
                )

        return images

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "parent",
            "text",
            "images",
            "created_at",
            "updated_at",
            "tags",
        )
        read_only_fields = ("user", "parent")

    def create(self, validated_data):
        images = validated_data.pop("images", None) or []
        post = super().create(validated_data)
        for image in images:
            PostImage.objects.create(post=post, image=image)
        return post


class PostCreateSerializer(PostSerializer):
    publish_at = serializers.DateTimeField(required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "parent",
            "text",
            "images",
            "created_at",
            "updated_at",
            "tags",
            "publish_at",
        )
        read_only_fields = ("user", "parent")


class PostListSerializer(
    TaggitSerializer,
    serializers.ModelSerializer,
):
    user = ProfileListSerializer(source="user.profile", read_only=True)
    parent = serializers.HyperlinkedRelatedField(
        view_name="posts:post-detail", read_only=True
    )
    images = PostImageListSerializer(many=True, read_only=True)
    tags = TagListSerializerField(
        child=serializers.CharField(
            allow_blank=True, allow_null=True, read_only=True
        ),
    )
    likes = serializers.IntegerField(source="like_count", read_only=True)
    replies = serializers.IntegerField(source="reply_count", read_only=True)

    class Meta:
        model = Post
        fields = (
            "url",
            "user",
            "parent",
            "text",
            "images",
            "likes",
            "replies",
            "created_at",
            "updated_at",
            "tags",
        )
        read_only_fields = ("user", "parent", "likes")
        extra_kwargs = {
            "url": {"view_name": "posts:post-detail"},
        }


class PostRetrieveSerializer(
    TaggitSerializer,
    serializers.ModelSerializer,
):
    user = ProfileListSerializer(source="user.profile", read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    parent = serializers.HyperlinkedRelatedField(
        view_name="posts:post-detail", read_only=True
    )
    likes = serializers.IntegerField(source="like_count", read_only=True)
    replies = serializers.IntegerField(source="reply_count", read_only=True)
    tags = TagListSerializerField(
        child=serializers.CharField(
            allow_blank=True, allow_null=True, read_only=True
        ),
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "parent",
            "text",
            "images",
            "likes",
            "replies",
            "created_at",
            "updated_at",
            "tags",
        )
