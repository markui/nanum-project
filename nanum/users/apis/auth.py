import crypt

from django.contrib.auth import get_user_model, authenticate
from django.core import signing
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import PasswordResetSerializer, PasswordResetConfirmSerializer, PasswordResetSendMailSerializer, \
    EmailUserSerializer
from ..serializers import SignupSerializer, LoginSerializer
from ..tasks import send_password_reset_email
from ipware import get_client_ip

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
        # ip 가져오기 실험 시작
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
        # Unable to get the client's IP address
            msg = {
                'error': "유저 IP를 가져오는 데 실패하였습니다"
            }
            return Response(msg, status=status.HTTP_204_NO_CONTENT)
        # The client's IP address is private
        # ip 가져오기 실험 끝
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
                'user': EmailUserSerializer(user).data,
                'token': token,
                'ip_address': client_ip
            }
            return Response(ret, status=status.HTTP_200_OK)


        # 인증에 실패한 경우
        else:
            msg = {
                'error': '존재하지 않는 계정입니다.'
            }
            return Response(msg, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetSendMailView(APIView):
    """
    이메일 가입 유저에게 비밀번호 재설정 링크를 담은 이메일 보내기
    Celery + Redis를 활용

    암호화: Django Signing + User Model DB에 password_reset_salt를 저장해,
    One-Time-Expire-Link 생성
    """

    def post(self, request):
        serializer = PasswordResetSendMailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = User.objects.get(email=email)
        # 유저의 토큰
        token = Token.objects.get_or_create(user=user)[0].key
        # Random Salt 생성 및 저장- One-Time-Expire-Link 를 위해
        random_password_salt = crypt.mksalt(crypt.METHOD_SHA512)
        user.password_reset_salt = random_password_salt
        user.save()
        # 유저의 pk + 토큰을 encode_value로 암호화
        # signing 모듈 + json serialization을 활용 (TimestampSigner 사용)
        uid = signing.dumps({'pk': user.pk})
        encode_value = signing.dumps({'token': token}, salt=random_password_salt)

        # 이메일에 보낼 html 내용
        html_content = render_to_string(
            'password_reset_email.html',
            {
                'email': email,
                'username': user.name,
                'url': 'localhost:4200/login/settings',
                'code': encode_value,
                'uid': uid

            }
        )
        # 이메일 미리보기에 보여질 text 내용
        text_content = strip_tags(html_content)

        # 이메일을 보내는 Celery Task 실행 (약 8초 소요)
        # Celery(Worker) + RabbitMQ(Broker)
        send_password_reset_email.delay(email, html_content, text_content)

        msg = {
            'message': f'비밀번호 재설정 링크가 담긴 이메일을 {email}로 전송하였습니다.',
            'email': f'{email}',
        }
        return Response(msg)


class PasswordResetConfirmView(APIView):
    """
    Client로부터 받은 임호화된 code(pk + 토큰)가 유효한지 확인하기
    1) 복호화 자체가 실패한 경우 (bad-signature)
        - 처음부터 잘못된 code인 경우
        - 재발급받아서 지난 코드가 유효하지 않게 된 경우
    2) 복호화는 성공했으나 유효하지 않은 경우 (expired-signature)
        - 암호화된 지 1일이 지난 code인 경우
    """

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        uid = serializer.validated_data['uid']
        try:
            # 해당 유저의 password_reset_salt 가져오기
            pk = signing.loads(uid, max_age=86400).get('pk')
            salt = User.objects.get(pk=pk).password_reset_salt
            # 해당 salt로 유저 토큰 복호화
            decode_value = signing.loads(code, salt=salt, max_age=86400)
        except signing.SignatureExpired:
            msg = {
                'error': '1일이 지나, 만료된 링크입니다. 비밀번호 재설정 이메일을 다시 받아주세요.',
                'type': 'expired-signature'
            }
        except signing.BadSignature:
            msg = {
                'error': '잘못된 링크입니다. 비밀번호 재설정 이메일을 다시 받아주세요.',
                'type': 'bad-signature'
            }
        else:
            token = decode_value['token']
            serializer = PasswordResetConfirmSerializer
            msg = {
                'pk': pk,
                'token': token,
                'type': 'success'
            }
            return Response(msg, status=status.HTTP_200_OK)

        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    pk, token, password1, password2를 request.data로 받아
    Token 인증을 마친 후, 해당 유저의 비밀번호를 재설정한다
    """

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 해당 토큰을 가진 유저 가져오기
        user = serializer.validated_data['token_model'].user
        # 유저의 비밀번호 업데이트하기 (hashing 하기)
        user.set_password(serializer.validated_data['password1'])
        user.save()
        msg = {
            'msg': '비밀번호 재설정에 성공하였습니다',
            'type': 'success'
        }
        return Response(msg)
