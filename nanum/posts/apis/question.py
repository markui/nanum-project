from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from posts.models import Question
from posts.utils.filters import QuestionFilter
from posts.utils.pagination import CustomPagination
from ..serializers.question import QuestionGetSerializer, QuestionPostSerializer, QuestionUpdateDestroySerializer, \
    QuestionFilterGetSerializer

__all__ = (
    'QuestionListCreateView',
    'QuestionMainFeedListView',
    'QuestionRetrieveUpdateDestroyView',
    'QuestionFilterListView',
)

User = get_user_model()


# 해당 유저의 모든 질문, 해당 유저가 답변한 질문, 해당 유저가 팔로우하는 질문, 해당 유저가 북마크하는 질문
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = QuestionFilter
    pagination_class = CustomPagination

    def filter_queryset(self, queryset):
        query_params = self.request.query_params.keys()
        value = self.request.query_params.values()
        filter_fields = self.filter_class.get_fields().keys() | {'ordering', 'page'}
        error = None

        if "" in list(value):
            error = {"message": "query parameter가 존재하나 value가 존재하지 않습니다."}

        elif query_params and not query_params <= filter_fields:
            error = {"message": "존재하지 않는 query_parameter입니다. "
                                "필터가 가능한 query_parameter는 다음과 같습니다:"
                                f"{filter_fields}"}
        else:
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, self)

        return error, queryset

    # POST
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuestionGetSerializer
        else:
            return QuestionPostSerializer

    def list(self, request, *args, **kwargs):
        """
        ListModelMixin의 list override
        filter_queryset 실행 시 error가 반환되었으면 error를 담은 400 BAD REQUEST를 반환

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        error, queryset = self.filter_queryset(self.get_queryset())
        if error:
            return Response(error, status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 해당 유저가 전문분야 설정에서 선택한 토픽들
class QuestionFilterListView(generics.ListAPIView):
    """
    queryset을 해당 유저가 전문분야 설정에서 선택한 토픽들을 리턴하는 queryset으로 재정의합니다.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionFilterGetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        user = self.request.user
        queryset = user.topic_expertise.all()
        # queryset = Question.objects.filter(topics__in=expertise_topics)
        # queryset = Topic.objects.filter(pk__in=expertise_topics)
        return queryset


# 내 질문을 제외한 전문분야, 관심분야 질문 리스트(main-feed)
class QuestionMainFeedListView(generics.ListAPIView):
    """
    queryset을 내 질문을 제외한 전문분야, 관심분야 질문 리스트를 리턴하는 queryset으로 재정의합니다.
    """
    serializer_class = QuestionGetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        user = self.request.user

        queryset = Question.objects.exclude(user=user)

        # 사용자가 선택한 전문분야, 관심분야 토픽
        topic_expertise = user.topic_expertise.values_list('id', flat=True)
        topic_interests = user.topic_interests.values_list('id', flat=True)
        # combine
        topics = topic_expertise | topic_interests
        # 사용자가 팔로우한 유저
        following_users = user.following.values_list('id', flat=True)

        topics_queryset = queryset & Question.objects.filter(topics__in=topics)
        following_users_queryset = queryset & Question.objects.filter(user__in=following_users)
        # queryset
        # queryset = (topics_queryset | following_users_queryset).distinct()
        queryset = (topics_queryset | following_users_queryset).order_by('-modified_at').distinct()
        return queryset


class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    질문에 대한 pk값으로 Question 객체 하나를 가져오거나 업데이트하거나 삭제하는 기능을 합니다.
    업데이트는 전체 input값을 모두 업데이트하는 PUT과 부분만 업데이트하는 PATCH를 지원합니다.
    """
    queryset = Question.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return QuestionUpdateDestroySerializer
        return QuestionGetSerializer
