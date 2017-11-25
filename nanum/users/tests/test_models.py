from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

User = get_user_model()

__all__ = (
    'UserModelTest',
)


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            email="abc@abc.com",
            password="12345678",
            is_superuser=True,
        )
        User.objects.create_user(
            name="김 경훈",
            email="abc1@abc.com",
            facebook_user_id=12345677,
            password="12345678",
        )
        User.objects.create_user(
            name="서상원",
            email="abc2@abc.com",
            password="12345678",
        )

    def test_user_create_user_method_non_superuser_facebook(self):
        """
        페이스북 유저 생성 테스트
        :return:
        """
        user_facebook = User.objects.create_user(
            name="유저",
            email="eee@eee.org",
            facebook_user_id=222222222,
            password="12345678",
        )
        self.assertIsInstance(user_facebook, User)

    def test_user_create_user_method_non_superuser_email(self):
        """
        이메일 유저 생성 테스트
        :return:
        """
        user_email = User.objects.create_user(
            name="유저",
            email="eee@eee.org",
            password="12345678",
        )
        self.assertIsInstance(user_email, User)

    def test_user_to_string_method(self):
        """
        User __str__ 함수 테스트
        :return:
        """
        super_user = User.objects.get(pk=1)
        user_facebook = User.objects.get(pk=2)
        user_email = User.objects.get(pk=3)
        self.assertEqual(str(super_user), "abc@abc.com")
        self.assertEqual(str(user_facebook), "12345677")
        self.assertEqual(str(user_email), "abc2@abc.com")

    def test_user_verbose_name_singular(self):
        """
        User Meta verbose_name 테스트
        :return:
        """
        super_user = User.objects.get(pk=1)
        field_label = super_user._meta.verbose_name
        self.assertEquals(field_label, _('user'))

    def test_user_verbose_name_plural(self):
        """
        User Meta verbose_name_plural 테스트
        :return:
        """
        super_user = User.objects.get(pk=1)
        field_label = super_user._meta.verbose_name_plural
        self.assertEquals(field_label, _('users'))

    def test_user_clean_method(self):
        """
        User Clean 함수 테스트

        :return:
        """
        pass

    def test_user_get_fullname_method(self):
        """
        User Full name 함수 테스트
        :return:
        """
        pass

    def test_user_email_user_method(self):
        pass
