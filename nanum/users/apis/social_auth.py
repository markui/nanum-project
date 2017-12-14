import requests
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import FacebookLoginSerializer

User = get_user_model()


class FacebookLoginView(APIView):
    """
    유저 페이스북 로그인

    클라이언트로부터 받는 정보
    1. access_token
    2. facebook_user_id

    를 바탕으로 디버깅하고, graph API로부터 허가받은 개인정보 요청

    scope: 'public_profile,email,user_friends'

    class DebugTokenInfo(NamedTuple):
        app_id: str
        application: str
        expires_at: int
        is_valid: bool
        scopes: list
        type: str
        user_id: str
        error: dict (오류날 경우)

    성공한 DebugTokenInfo 예시)

    {'data': {'app_id': '1846495555661501',
          'application': 'insta-project',
          'expires_at': 1511967600,
          'is_valid': True,
          'scopes': ['user_friends', 'email', 'public_profile'],
          'type': 'USER',
          'user_id': '1478236202297666'}}

    성공한 Graph User Info 예시)

    {'age_range': {'min': 21},
     'gender': 'male',
     'id': '1478236202297666',
     'name': '김경훈',
     'picture': {'data': {'height': 50,
                          'is_silhouette': False,
                          'url': 'https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/19366151_1361082024013085_6233548507437295536_n.jpg?oh=8264c6a03574e5123537370974b4480b&oe=5AA2BFA1',
                          'width': 50}}}
    """

    def post(self, request):
        serializer = FacebookLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 클라이언트로부터 도착한 2개의 페이스북 인증 value
        access_token = serializer.validated_data['access_token']
        facebook_user_id = serializer.validated_data['facebook_user_id']

        def get_debug_token_info(token):
            app_id = settings.FACEBOOK_APP_ID
            app_secret_code = settings.FACEBOOK_APP_SECRET_CODE
            app_access_token = f'{app_id}|{app_secret_code}'
            url_debug_token = 'https://graph.facebook.com/debug_token'
            params_debug_token = {
                'input_token': token,
                'access_token': app_access_token,
            }
            response = requests.get(url_debug_token, params_debug_token)
            return response.json()

        # request.data로 전달된 access_token값을 페이스북API쪽에 debug요청, 결과를 받아옴
        # 웹 액세스 토큰 만기 확인: 수명 약 2시간
        debug_token_info = get_debug_token_info(access_token)
        print(debug_token_info)
        if debug_token_info.get('error'):
            raise APIException(debug_token_info.get('error').get('message'))

        if not debug_token_info['data']['is_valid']:
            raise APIException('페이스북 토큰이 유효하지 않음')

        if debug_token_info['data']['user_id'] != facebook_user_id:
            raise APIException('페이스북 토큰의 사용자와 전달받은 facebook_user_id가 일치하지 않음')

        # access token을 바탕으로, Grapth API에 유저정보 요청해서 가져오기
        user_info_fields = [
            'id',
            'name',
            'picture',
            'age_range',
            'gender',
            'email',
            # 'hometown',
            # 'education',
            # 'work',
            # 'location',
            # 'birthday',
            # 'friendlists'
        ]

        url_graph_user_info = 'https://graph.facebook.com/me'
        params_graph_user_info = {
            'fields': ','.join(user_info_fields),
            'access_token': access_token,
        }

        # access token을 바탕으로, Graph API에 유저정보 요청해서 가져오기
        response = requests.get(url_graph_user_info, params_graph_user_info)
        graph_user_info = response.json()
        # Facebook Custom Backend Authentication
        user = authenticate(facebook_user_id=facebook_user_id)
        # 가입하지 않은 유저인 경우
        if not user:
            user = User.objects.create_user(
                facebook_user_id=facebook_user_id,
                user_type='FB',
                name=graph_user_info['name'] or '',
            )
            # user.profile.profile_image = graph_user_info['picture']['data']['url']
            user.profile.gender = graph_user_info['gender'] or ''
            user.profile.save()

        ret = {
            'token': Token.objects.get_or_create(user=user)[0].key
        }
        return Response(ret, status=status.HTTP_200_OK)
