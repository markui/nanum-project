from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'User',
)

from django.contrib.auth.base_user import BaseUserManager


# Custom User Manager
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, facebook_user_id, password, **extra_fields):
        """
        Creates and saves a User with the given
        email OR facebook_user_id
        and password.
        """
        # 반드시 email, facebook_user_id 둘 중 하나의 값은 있어야 한다
        if not email and not facebook_user_id:
            raise ValueError('The given email or facebook_user_id must be set')

        # email, facebook_user_id 둘 중 하나의 값이 None이 아닌 경우
        # 만일 None인 값이 있으면 이를 ''로 바꿔준다 (필드 null=False이기 때문)
        facebook_user_id = facebook_user_id or ''
        email = self.normalize_email(email)

        user = self.model(email=email, facebook_user_id=facebook_user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, facebook_user_id=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, facebook_user_id, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    """
    하나의 유저는 반드시 email 혹은 facebook_user_id 둘 중
    적어도 하나의 필드에는 값이 들어가 있어야 한다.

    email, facebook_user_id 모두 unique 하다.
    따라서, 같은 이메일 혹은 같은 페이스북 유저 ID를 가진 유저는 존재할 수 없다.

    예시) 이미 이메일 가입을 한 유저가, 후에 같은 이메일이 등록된 페이스북 ID로 소셜 로그인을 한 경우,
    새로운 유저가 만들어지지 않고, 기존의 유저로 로그인하며, 페이스북 관련 정보만을 추가시킨다.

    """
    # Model Fields
    # 인증
    FACEBOOK = 'FB'
    EMAIL = 'EM'
    USER_TYPE_CHOICES = (
        (FACEBOOK, 'Facebook'),
        (EMAIL, 'Email'),
    )

    email = models.EmailField(_('email address'), unique=True, blank=True)
    facebook_user_id = models.PositiveIntegerField(_('facebook user id'), unique=True, blank=True)

    user_type = models.CharField(
        max_length=1,
        choices=USER_TYPE_CHOICES,
        default=EMAIL,
    )

    # 이름
    name = models.CharField(_('full name'), max_length=30)

    # 전문분야 주제
    topic_expertise = models.ManyToManyField(
        'topics.Topic',
        related_name='users_with_expertise',
    )

    # 관심분야 주제
    topic_interests = models.ManyToManyField(
        'topics.Topic',
        related_name='users_with_interest',
    )

    # 유저 활동
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    # User Manager
    objects = UserManager()

    # Django 기본 Model Backend authenticate()에서,
    # 기존의 username을 대신할 필드
    # ex) 구) authenticate(username='mark', password='12345')
    # ex) 신) authenticate(email='mark@gmail.com', password='12345')
    USERNAME_FIELD = 'email'
    # createsuperuser 커맨드 실행시 요구하는 필드
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.facebook_user_id

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s' % (self.name)
        return full_name.strip()

    # def get_short_name(self):
    #     "Returns the short name for the user."
    #     return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
