import os
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from django_countries.fields import CountryField

from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.username


def generate_file_name(info, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(info)}-{uuid.uuid4()}{extension}"

    return filename


def profile_picture_file_path(instance, filename):
    filename = generate_file_name(instance.user.username, filename)

    return os.path.join("uploads/profile_pictures/", filename)


class Profile(models.Model):
    class GenderChoices(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    picture = models.ImageField(
        upload_to=profile_picture_file_path,
        null=True,
        blank=True,
    )
    bio = models.CharField(max_length=160, blank=True)
    gender = models.CharField(
        max_length=32,
        choices=GenderChoices.choices,
        blank=True,
    )
    country = CountryField(blank=True)
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="following",
    )

    def __str__(self) -> str:
        return str(self.user)

    @property
    def follower_count(self) -> int:
        return self.followers.count()

    @property
    def following_count(self) -> int:
        return self.following.count()
