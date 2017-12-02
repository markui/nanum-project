from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import InterestFollowRelation, ExpertiseFollowRelation, UserFollowRelation, QuestionFollowRelation
from users.serializers.relation.follow import UserFollowRelationSerializer, QuestionFollowRelationSerializer
from users.utils.permissions import IsFollower
from ...serializers import TopicFollowRelationSerializer

User = get_user_model()

__all__ = (
    # Topic Follow
    'InterestFollowRelationCreateView',
    'InterestFollowRelationDetailView',
    'ExpertiseFollowRelationCreateView',
    'ExpertiseFollowRelationDetailView',
    # User Follow
    'UserFollowRelationCreateView',
    'UserFollowRelationDetailView',
    # Question Follow
    'QuestionFollowRelationCreateView',
    'QuestionFollowRelationDetailView',
)


# Topic Follow
class InterestFollowRelationCreateView(APIView):
    """
    유저 - 관심분야 주제 팔로우 관계 생성
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = TopicFollowRelationSerializer(data=request.data, context={'request': request, 'type': 'interest'})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        # 유저 - 관심주제 팔로우 성공했을 경우
        return Response(status=status.HTTP_201_CREATED)


class InterestFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 관심분야 주제 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsFollower,
    )

    queryset = InterestFollowRelation.objects.all()
    serializer_class = TopicFollowRelationSerializer


class ExpertiseFollowRelationCreateView(APIView):
    """
    유저 - 전문분야 주제 팔로우 관계 생성
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = TopicFollowRelationSerializer(data=request.data, context={'request': request, 'type': 'expertise'})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        # 유저 - 관심주제 팔로우 성공했을 경우
        return Response(status=status.HTTP_201_CREATED)


class ExpertiseFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 전문분야 주제 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsFollower,
    )

    queryset = ExpertiseFollowRelation.objects.all()
    serializer_class = TopicFollowRelationSerializer


# User Follow
class UserFollowRelationCreateView(APIView):
    """
    유저 - 다른 유저 팔로우 관계 생성
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = UserFollowRelationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        # 유저 - 다른 유저 팔로우 성공했을 경우
        return Response(status=status.HTTP_201_CREATED)


class UserFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 유저 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsFollower,
    )

    queryset = UserFollowRelation.objects.all()
    serializer_class = UserFollowRelationSerializer


# Question Follow
class QuestionFollowRelationCreateView(APIView):
    """
    유저 - 다른 유저 팔로우 관계 생성
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = QuestionFollowRelationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        # 유저 - 다른 유저 팔로우 성공했을 경우
        return Response(status=status.HTTP_201_CREATED)


class QuestionFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 질문 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsFollower,
    )

    queryset = QuestionFollowRelation.objects.all()
    serializer_class = QuestionFollowRelationSerializer
