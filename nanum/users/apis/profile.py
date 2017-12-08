from rest_framework import generics

from users.models import Profile
from users.serializers import ProfileSerializer


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    유저 프로필 detail 정보 가져오기 / 업데이트하기
    """
    queryset = Profile.objects.all()
    lookup_url_kwarg = 'pk'
    lookup_field = 'user'

    serializer_class = ProfileSerializer

