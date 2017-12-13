from django.contrib.auth import get_user_model, authenticate
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import PasswordResetSerializer
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
        # Model Backend Authentication
        # 존재하는 유저 & is_active=True 인지 Authenticate
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


class PasswordResetView(APIView):
    """
    이메일 가입 유저에게 비밀번호 재설정 링크를 담은 이메일 보내기
    Celery + Redis를 활용
    """

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        # 비밀번호 재설정 링크를 담은 이메일 보내기
        # Celery Task로 해결 (Worker: Redis)

        msg = {
            'message': f'비밀번호 재설정 링크가 담긴 이메일을 {email}로 전송하였습니다.',
            'email': f'{email}',
        }
        return Response(msg)


class PasswordResetConfirmView(APIView):
    """
    Client로부터 받은 유저 토큰을 인증한 후, 유저 비밀번호 바꾸기
    Accepts the following POST parameters:
    token, uid, new_password1, new_password2
    """

    pass
