from django.contrib.auth import get_user_model

User = get_user_model()


class FacebookBackend:
    def authenticate(self, request, facebook_user_id):
        try:
            return User.objects.get(facebook_user_id=facebook_user_id)
        except User.DoesNotExist:
            return None

    # 필수
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
