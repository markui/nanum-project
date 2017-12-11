from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from users.models import Profile, EmploymentCredential, EducationCredential
from users.serializers import ProfileSerializer, EmploymentCredentialSerializer, EducationCredentialSerializer
from users.utils.permissions import IsOwnerOrReadOnly, IsProfileOwnerOrReadOnly


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    유저 프로필의 main-detail 정보 가져오기/업데이트하기
    """
    queryset = Profile.objects.all()
    lookup_url_kwarg = 'pk'
    lookup_field = 'user'

    serializer_class = ProfileSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )


class EmploymentCredentialListCreateView(generics.ListCreateAPIView):
    """
    유저 프로필의 경력 정보 List하기/생성하기
    경력 생성의 경우, 해당 프로필 url의 pk에 해당하는 user와 request를 한 user가 일치할때만 가능
    경력 리스트의 경우 누구나 request 가능
    """
    serializer_class = EmploymentCredentialSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsProfileOwnerOrReadOnly,
    )

    def get_queryset(self):
        try:
            profile = Profile.objects.get(user=self.kwargs.get('pk'))
        except Profile.DoesNotExist:
            raise Http404
        else:
            return EmploymentCredential.objects.filter(profile=profile)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class EmploymentCredentialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    유저 프로필의 특정 경력 정보 가져오기/수정하기/삭제하기
    """
    queryset = EmploymentCredential.objects.all()
    lookup_url_kwarg = 'credential_pk'
    lookup_field = 'pk'

    serializer_class = EmploymentCredentialSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsProfileOwnerOrReadOnly,
    )


class EducationCredentialListCreateView(generics.ListCreateAPIView):
    """
    유저 프로필의 학력 정보 List하기/생성하기
    학력 생성의 경우, 해당 프로필 url의 pk에 해당하는 user와 request를 한 user가 일치할때만 가능
    학력 리스트의 경우 누구나 request 가능
    """
    serializer_class = EducationCredentialSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsProfileOwnerOrReadOnly,
    )

    def get_queryset(self):
        try:
            profile = Profile.objects.get(user=self.kwargs.get('pk'))
        except Profile.DoesNotExist:
            raise Http404
        else:
            return EducationCredential.objects.filter(profile=profile)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class EducationCredentialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    유저 프로필의 특정 학력 정보 가져오기/수정하기/삭제하기
    """
    queryset = EducationCredential.objects.all()
    lookup_url_kwarg = 'credential_pk'
    lookup_field = 'pk'

    serializer_class = EducationCredentialSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsProfileOwnerOrReadOnly,
    )


class ProfileStatsRetrieveView(generics.RetrieveAPIView):
    """
    유저 프로필의 Activity Stats(활동 통계) 가져오기
    """
    pass
