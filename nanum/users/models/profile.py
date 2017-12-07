from django.conf import settings
from django.db import models
from django.utils import timezone

__all__ = (
    'Profile',
    'EducationCredentials',
    'EmploymentCredentials',
)

User = settings.AUTH_USER_MODEL

HIGHSCHOOL = 'HS'
BACHELOR = 'BA'
MASTERS = 'MA'
DOCTORATE = 'PHD'

DEGREES = (
    (HIGHSCHOOL, '고등학교'),
    (BACHELOR, '대학교'),
    (MASTERS, '석사과정'),
    (DOCTORATE, '박사과정')
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
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)

    # 여러 credential 중에서 다른 유저들에게 메인으로 표시될 필드
    main_credential = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=2000, blank=True)

    # facebook 그래프 API로 가져온 정보
    gender = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f'Profile of {self.user}'


class EducationCredentials(models.Model):
    """
    유저 프로필에 들어가는 학력
    """
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name="education_credentials")
    school = models.ForeignKey('topics.Topic', on_delete=models.SET_NULL, blank=True, null=True,
                               related_name="school_credentials")
    # 전공
    concentration = models.ForeignKey('topics.Topic', on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name="concentration_credentials")
    # 학위
    degree_type = models.CharField(choices=DEGREES, max_length=3, blank=True)
    graduation_year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)


class EmploymentCredentials(models.Model):
    """
    유저 프로필에 들어가는 이력
    """
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name="employment_credentials")
    position = models.CharField(max_length=50, blank=True)
    company = models.ForeignKey('topics.Topic', on_delete=models.SET_NULL, blank=True, null=True,
                                related_name="company_credentials")

    start_year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    end_year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    working_status = models.BooleanField(default=False)
