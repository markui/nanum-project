from django.contrib.auth import get_user_model
from django.db import models

__all__ = [
    'Profile'
]

User = get_user_model()
DEGREES = (
    ('', ''),
    ('', ''),
    ('', '')
)


class Profile(models.Model):
    """
    유저 프로필 정보
    """
    user = models.OneToOneField(
        User,
        primary_key=True,
        on_delete=models.CASCADE,
    )
    profile_image = models.ImageField(
        null=True,
        blank=True,
    )
    main_credential = models.CharField(
        max_length=100,
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
    )


class EducationCredentials(models.Model):
    """
    유저 프로필에 들어가는 학력 정보
    """
    user = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name="education_credentials",
    )
    # school = models.ForeignKey(
    #     'topics.Topic',
    # )
    # concentration = models.ForeignKey(
    #     'topics.Topic',
    # )
    degree_type = models.CharField(
        choices=DEGREES,
    )
    graduation_year = models.DateField()


class EmploymentCredentials(models.Model):
    """
    유저 프로필에 들어가는 고용정보
    """
    user = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name="employment_credentials",
    )
    # position = models.ForeignKey(
    #     'topics.Topic'
    # )
    # company = models.ForeignKey(
    #     'topics.Topic'
    # )
    start_year = models.DateField()
    end_year = models.DateField()
    working_status = models.BooleanField()
