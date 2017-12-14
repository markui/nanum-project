from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
UserModel = get_user_model()


class FacebookBackend:
    def authenticate(self, request, facebook_user_id):
        try:
            return UserModel.objects.get(facebook_user_id=facebook_user_id)
        except UserModel.DoesNotExist:
            return None

    # 필수
    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class EmailBackend(ModelBackend):
    """
    페이스북 로그인을 처음으로 하는 미가입 유저의 경우,
    차례대로 Authentication Backend를 순서대로 훑는다.
    이 때, USERNAME_FIELD인 email이 빈 계정을 중복해서 찾으려고
    하는 것을 방지하기 위해, email이 kwargs에 오지 않은 경우, 즉
    페이스북 authentication을 하려는 경우, 바로 None을 return한다.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            if not kwargs.get(UserModel.USERNAME_FIELD):
                return None
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user