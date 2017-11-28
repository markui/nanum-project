from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from .serializers import SignupSerializer

User = get_user_model()


class SignupView(CreateAPIView):
    """
    유저 이메일 회원가입
    """
    queryset = User.objects.all()
    serializer_class = SignupSerializer


class LoginView(CreateAPIView):
    """
    유저 이메일 로그인
    """
    pass
