from django.contrib.auth import get_user_model, authenticate
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import SignupSerializer, LoginSerializer

User = get_user_model()


class SignupView(generics.CreateAPIView):
    """
    유저 이메일 회원가입
    """
    serializer_class = SignupSerializer


class LoginView(APIView):
    """
    유저 이메일 로그인(토큰 생성/반환)
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer가 valid 하면,
        # 존재하는 유저인지 Authenticate
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        # 인증에 성공한 경우
        if user:
            # 토큰 생성/반환
            token = Token.objects.get_or_create(user=user)[0].key
            # print(token)
            ret = {
                'token': token
            }
            return Response(ret, status=status.HTTP_200_OK)


        # 인증에 실패한 경우
        else:
            msg = {
                'error': '존재하지 않는 계정입니다.'
            }
            return Response(msg, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetEmailView(APIView):
    """
    이메일 가입 유저 - 비밀번호 재설정 이메일 보내기
    Celery + Redis를 활용
    """

    pass
