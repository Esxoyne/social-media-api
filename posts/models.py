import os
import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from taggit.managers import TaggableManager


class Post(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        related_name="posts",
        null=True,
        on_delete=models.SET_NULL,
    )
    parent = models.ForeignKey(
        "self",
        related_name="replies",
        null=True,
        on_delete=models.CASCADE,
        default=None,
    )
    text = models.CharField(max_length=300)
    likes = models.ManyToManyField(
        get_user_model(),
        related_name="post_likes",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user}: {self.text}"

    @property
    def like_count(self) -> int:
        return self.likes.count()

    @property
    def reply_count(self) -> int:
        return self.replies.count()


def generate_file_name(info, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(info)}-{uuid.uuid4()}{extension}"

    return filename


def post_image_file_path(instance, filename):
    filename = generate_file_name(instance.post.text[:30], filename)

    return os.path.join("uploads", "post_images", filename)


class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to=post_image_file_path,
    )

    def __str__(self):
        return f"{self.id}: {self.post}"
