import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

__all__ = (
    'UserModelTest',
)


class UserModelTest(TestCase):
    # @classmethod
    # def setUpTestData(cls):
    #     superuser = User.objects.create_superuser(
    #         email="abc@abc.com",
    #         password="12345678",
    #         name="슈퍼유저",
    #         is_superuser=True,
    #     )

    def test_user_create_user_method_non_superuser_facebook(self):
        user = User.objects.create_user(
            name="유저",
            facebook_user_id=1234567,
            password="abc123",
        )
        self.assertIsInstance(user, User, msg="user 객체이며 페이스북 유저")

    def test_user_create_user_method_non_superuser_email(self):
        pass

    def test_user_to_string_method(self):
        pass

    def test_user_verbose_name(self):
        pass

    def test_user_verbose_name_plural(self):
        pass

    def test_user_clean_method(self):
        pass

    def test_user_get_fullname_method(self):
        pass

    def test_user_email_user_method(self):
        pass
