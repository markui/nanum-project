from django.conf import settings
from django.db import models
from django.utils import timezone

from utils import rescale
from ..utils import (
    user_img_path,
    user_thumb_img_25_path,
    user_thumb_img_50_path,
    user_thumb_img_200_path
)

__all__ = (
    'Profile',
    'EmploymentCredential',
    'EducationCredential',
)

User = settings.AUTH_USER_MODEL

HIGHSCHOOL = 'HS'
BACHELOR = 'BA'
MASTERS = 'MA'
DOCTORATE = 'PHD'

DEGREES = (
    (HIGHSCHOOL, '고등학교'),
    (BACHELOR, '학사'),
    (MASTERS, '석사'),
    (DOCTORATE, '박사')
)

# 1900 ~ 현재 연도
YEAR_CHOICES = [
    (year, year)
    for year
    in range(1900, timezone.now().year + 1)
]


class Profile(models.Model):
    """
    유저 프로필 정보

    Frontend Client: scope=[public_profile,user_friends,email]

    facebook 그래프 API로 가져온 정보:

    {
     'gender': 'male', => (Profile: gender)
     'id': '1478236202297666', => (User: facebook_user_id)
     'name': '김경훈', => (User: name)
     'picture': {'data': {'height': 50,
                          'is_silhouette': False,
                          'url': 'https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/19366151_1361082024013085_6233548507437295536_n.jpg?oh=8264c6a03574e5123537370974b4480b&oe=5AA2BFA1',
                          'width': 50}} => (Profile: profile_image)
    }
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_img_path, blank=True, null=True)
    # A * A 픽셀별 썸네일 이미지
    thumbnail_image_200 = models.ImageField(upload_to=user_thumb_img_200_path, blank=True, null=True)
    thumbnail_image_50 = models.ImageField(upload_to=user_thumb_img_50_path, blank=True, null=True)
    thumbnail_image_25 = models.ImageField(upload_to=user_thumb_img_25_path, blank=True, null=True)

    # 여러 credential 중에서 다른 유저들에게 메인으로 표시될 필드
    main_credential = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=2000, blank=True)

    # facebook 그래프 API로 가져온 정보
    gender = models.CharField(max_length=30, blank=True)

    # relation 에서 가져온 정보 - 누적되는 팔로워/팔로잉 수
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)

    def __str__(self):
        return f'Profile of {self.user}'

    # 유저가 이미지를 업로드 할 시
    # 200 * 200 / 50 * 50 / 25 * 25의 rescale된 썸네일 이미지들 역시 별도의 필드에 저장됨
    def save(self, *args, **kwargs):
        status = kwargs.pop('status', None)
        if self.image:
            # ProfileSerializer update에서, image를 제외한 다른
            # Profile 필드들을 새로 업데이트하는 경우 resizing을 실시하지 않는다
            if status != 'same-image':
                image_file_byte_data = self.image.read()
                thumbnail_image_file_200 = rescale(image_file_byte_data, 200, 200, force=True)
                thumbnail_image_file_50 = rescale(image_file_byte_data, 50, 50, force=True)
                thumbnail_image_file_25 = rescale(image_file_byte_data, 25, 25, force=True)

                self.thumbnail_image_200.save(f'{self.image.name}', thumbnail_image_file_200, save=False)
                self.thumbnail_image_50.save(f'{self.image.name}', thumbnail_image_file_50, save=False)
                self.thumbnail_image_25.save(f'{self.image.name}', thumbnail_image_file_25, save=False)

        super().save(*args, **kwargs)


class EmploymentCredential(models.Model):
    """
    유저 프로필에 들어가는 이력
    """
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name="employment_credentials")
    company = models.ForeignKey('topics.Topic', on_delete=models.SET_NULL, blank=True, null=True,
                                related_name="company_credentials")
    position = models.CharField(max_length=50, blank=True)
    start_year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    end_year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    working_status = models.BooleanField(default=False)


class EducationCredential(models.Model):
    """
    유저 프로필에 들어가는 학력
    """
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name="education_credentials")
    school = models.ForeignKey('topics.Topic', on_delete=models.SET_NULL, blank=True, null=True,
                               related_name="school_credentials")
    # 전공
    concentration = models.ForeignKey('topics.Topic', on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name="concentration_credentials")
    # 학위
    degree_type = models.CharField(choices=DEGREES, max_length=3, blank=True)
    graduation_year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
