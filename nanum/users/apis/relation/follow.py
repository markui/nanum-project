from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import InterestFollowRelation, ExpertiseFollowRelation, UserFollowRelation, QuestionFollowRelation
from users.serializers.relation.follow import UserFollowRelationSerializer, QuestionFollowRelationSerializer, \
    UserFollowParticipantSerializer, FollowingTopicSerializer
from users.utils.pagination import UserFollowParticipantPagination, FollowingTopicPagination
from users.utils.permissions import IsUserWhoTookAction
from ...serializers import TopicFollowRelationSerializer

User = get_user_model()

__all__ = (
    # Topic Follow
    'InterestFollowRelationCreateView',
    'InterestFollowRelationDetailView',
    'ExpertiseFollowRelationCreateView',
    'ExpertiseFollowRelationDetailView',
    'FollowingInterestListView',
    'FollowingExpertiseListView',
    # User Follow
    'UserFollowRelationCreateView',
    'UserFollowRelationDetailView',
    'UserFollowerListView',
    'UserFollowingListView',
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
        print(request.data)
        serializer = TopicFollowRelationSerializer(data=request.data, context={'request': request, 'type': 'interest'})
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save(user=request.user)
        # 유저 - 관심주제 팔로우 성공했을 경우
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InterestFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 관심분야 주제 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsUserWhoTookAction,
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpertiseFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 전문분야 주제 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsUserWhoTookAction,
    )

    queryset = ExpertiseFollowRelation.objects.all()
    serializer_class = TopicFollowRelationSerializer


class MultipleInterestFollowRelationCreateView(generics.CreateAPIView):
    """
    회원가입 직후, "주제 설정 페이지" 에서
    유저 - 관심분야 주제 다중 팔로우하기
    """
    pass


class MultipleExpertiseFollowRelationCreateView(generics.CreateAPIView):
    """
    회원가입 직후, "주제 설정 페이지" 에서
    유저 - 전문분야 주제 다중 팔로우하기
    """
    pass


class FollowingInterestListView(generics.ListAPIView):
    """
    유저가 팔로우하는 관심분야 주제 가져오기
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowingTopicSerializer
    pagination_class = FollowingTopicPagination

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return user.topic_interests.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        오버라이드를 하여 serializer에게 "관심분야" type이라는 정보를 전달
        """
        context = super().get_serializer_context()
        context.update({'topic_type': 'interest'})
        return context


class FollowingExpertiseListView(generics.ListAPIView):
    """
    유저가 팔로우하는 전문분야 주제 가져오기
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowingTopicSerializer
    pagination_class = FollowingTopicPagination

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return user.topic_expertise.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        오버라이드를 하여 serializer에게 "전문분야" type이라는 정보를 전달
        """
        context = super().get_serializer_context()
        context.update({'topic_type': 'expertise'})
        return context


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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 유저 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsUserWhoTookAction,
    )

    queryset = UserFollowRelation.objects.all()
    serializer_class = UserFollowRelationSerializer


class UserFollowerListView(generics.ListAPIView):
    """
    유저의 팔로워 리스트를 가져오기
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowParticipantSerializer
    pagination_class = UserFollowParticipantPagination

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return user.followers.all()


class UserFollowingListView(generics.ListAPIView):
    """
    유저가 팔로우하는 사용자 리스트를 가져오기
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowParticipantSerializer
    pagination_class = UserFollowParticipantPagination

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return user.following.all()


# Question Follow
class QuestionFollowRelationCreateView(APIView):
    """
    유저 - 질문 팔로우 관계 생성
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = QuestionFollowRelationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        # 유저 - 다른 유저 팔로우 성공했을 경우
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionFollowRelationDetailView(generics.RetrieveDestroyAPIView):
    """
    유저 - 질문 팔로우 관계 가져오기 / 삭제하기
    """
    permission_classes = (
        IsAuthenticated,
        IsUserWhoTookAction,
    )

    queryset = QuestionFollowRelation.objects.all()
    serializer_class = QuestionFollowRelationSerializer
