from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.exceptions import ParseError

from utils.permissions import IsAuthorOrAuthenticatedReadOnly
from ..models import Answer
from ..serializers.answer import AnswerUpdateSerializer, AnswerPostSerializer, AnswerGetSerializer
from ..utils.filters import AnswerFilter
from ..utils.pagination import ListPagination

__all__ = (
    'AnswerListCreateView',
    'AnswerRetrieveUpdateDestroyView',
    'AnswerMainFeedListView',
)

User = get_user_model()


class AnswerListCreateView(generics.ListCreateAPIView):
    """
    유저가 작성한 Answer들을 갖고와주는 ListAPIView 와
    QuillJS Content를 저장해주는 CreateAPIView
    Filter Class를 적용하여 Topic, Bookmarked, User에 대한 필터링과
    created_at, modified_at을 이용하여 ordering을 결정할 수 있음
    """
    queryset = Answer.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AnswerFilter
    pagination_class = ListPagination

    def filter_queryset(self, queryset):
        """
        GenericAPIView의 filter_queryset override
        필터가 가능한 queryset이면 필터를 실시, 그 외의 경우에는 에러 메세지를 반환
        :param queryset: View의 queryset
        """
        query_params = self.request.query_params.keys()
        values = self.request.query_params.values()
        filter_fields = self.filter_class.get_fields().keys() | {'ordering', 'page'}
        error = None

        # 만약 query parameter가 왔는데 value가 오지 않았을 경우
        # 혹은 query parameter가 왔는데 존재하지 않는 query parameter인 경우
        if "" in list(values):
            error = {"error": "query parameter가 존재하나 value가 존재하지 않습니다."}
        if query_params and not query_params <= filter_fields:
            error = {"error": "존재하지 않는 query_parameter입니다. "
                              "필터가 가능한 query_parameter는 다음과 같습니다:"
                              f"{filter_fields}"}
        if error:
            raise ParseError(detail=error)

        return super().filter_queryset(queryset)

    def get_serializer(self, *args, **kwargs):
        """
        GenericAPIView의 get_serializer override
        POST요청과 GET요청을 나누어 Serializer 종류를 변경
        :param args:
        :param kwargs:
        :return:
        """
        if self.request.method == 'POST':
            serializer_class = AnswerPostSerializer
        else:
            serializer_class = AnswerGetSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class AnswerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Answer Retrieve, Update, Destroy API View
    Author 일 경우 Update, Destroy가 가능하고 Authenticated 일 경우 Get이 가능
    """
    queryset = Answer.objects.all()
    permission_classes = (
        IsAuthorOrAuthenticatedReadOnly,
    )

    def get_serializer(self, *args, **kwargs):
        """
        GenericAPIView get_serializer override
        PUT, PATCH와 GET요청을 나누어 Serializer 종류를 변경
        :param args:
        :param kwargs:
        :return:
        """
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = AnswerUpdateSerializer
        else:
            serializer_class = AnswerGetSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class AnswerMainFeedListView(generics.ListAPIView):
    """
    유저를 위한 주 답변 Feed
    1. Topic, Follower를 기반으로 개인화된 피드 생성
    2. +추후 Like 정보 추가
    3. +추후 CF Filtering / Content-based Filtering 적용
    """
    serializer_class = AnswerGetSerializer
    authentication_classes = (
        permissions.IsAuthenticated,
    )
    pagination_class = ListPagination

    def get_queryset(self):
        """
        GenericAPIView의 get_queryset override
        Queryset을 필터하여 피드에 들어갈 내용을 반환
        :return:
        """
        user = self.request.user

        # Get all Topics that user is following
        answer_topic_interest = user.topic_interests.values_list('id', flat=True)
        answer_topic_expertise = user.topic_expertise.values_list('id', flat=True)

        # Combine both
        answer_topic = answer_topic_interest | answer_topic_expertise

        # Get Follower's Answers
        following_users = user.following.values_list(flat=True)

        # Filter Answer, order by the most recently modified post
        queryset = Answer.objects.filter(topic__in=answer_topic) \
            .filter(user__in=following_users) \
            .order_by('modified_at')

        if not queryset:
            queryset = Answer.objects.all()

        return queryset
