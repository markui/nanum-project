from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import generics, permissions

from ..models import Answer
from ..serializers.answer import AnswerSerializer, AnswerFeedSerializer

__all__ = (
    'AnswerListCreateView',
    'AnswerMainFeedListView',
    'AnswerBookmarkFeedListView',
    'AnswerFilterFeedListView',
)


class AnswerListCreateView(generics.ListCreateAPIView):
    """
    유저가 작성한 Answer들을 갖고와주는 ListCreate API
    """
    queryset = Answer
    serializer_class = AnswerSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        user = self.request.user
        return user.answer_set.all()

    def create(self, request, *args, **kwargs):
        """
        Request에서 quill.js json 파일을 content로 받음
        사진 관련 파일에 대해 bytecode parsing -> save as jpg to S3 -> convert bytecode to S3 link
        변환된 데이터를 가지고 Answer 객체 생성
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return super().create(request, *args, **kwargs)


class AnswerMainFeedListView(generics.ListAPIView):
    """
    유저를 위한 주 답변 Feed
    1. Topic, Follower를 기반으로 개인화된 피드 생성
    2. +추후 Like 정보 추가
    3. +추후 CF Filtering / Content-based Filtering 적용
    """
    serializer_class = AnswerFeedSerializer

    def get_queryset(self):
        """
        Topic, Follower 기반 filter된 queryset 반환
        :return:
        """
        user = self.request.user

        # Get all Topics that user is following
        answer_topic_interest = list(user.topic_interests.values_list(flat=True))
        answer_topic_expertise = list(user.topic_expertise.values_list(flat=True))

        # Combine both
        answer_topic = answer_topic_interest.extend(answer_topic_expertise)

        # Get Follower's Answers
        following_users = user.following.values_list(flat=True)

        # Filter Answer, order by the most recently modified post
        queryset = Answer.objects.filter(topic__in=answer_topic) \
            .filter(user__in=following_users) \
            .order_by('modified_at')

        return queryset


class AnswerBookmarkFeedListView(generics.ListAPIView):
    """
    유저가 북마크한 답변 필터 목록
    """
    queryset = Answer
    serializer_class = AnswerFeedSerializer

    def get_queryset(self):
        user = self.request.user
        return user.bookmarked_questions.all()


class AnswerFilterFeedListView(generics.ListAPIView):
    """
    최신 + Topic Filter
    """
    queryset = Answer
    serializer_class = AnswerFeedSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('topic')
    ordering_fields = ('modified_at')
