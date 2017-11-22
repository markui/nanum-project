from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

User = get_user_model()



class User(AbstractUser):
    # 추가된 필드
    profile_image = models.ImageField(
        null=True,
        blank=True,
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
    )
    # education_credentials =
    # employment_credentials =
