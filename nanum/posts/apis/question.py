from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from posts.models import Question
from posts.utils.filters import QuestionFilter
from posts.utils.pagination import CustomPagination
from ..serializers.question import QuestionGetSerializer, QuestionPostSerializer, QuestionUpdateDestroySerializer

__all__ = (
    'QuestionListCreateView',
    'QuestionMainFeedListView',
    'QuestionRetrieveUpdateDestroyView',
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
        filter_fields = self.filter_class.get_fields().keys() | {'ordering'}
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


# 내 질문을 제외한 전문분야, 관심분야 질문 리스트(main-feed)
class QuestionMainFeedListView(generics.ListAPIView):
    serializer_class = QuestionGetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        user = self.request.user

        queryset = Question.objects.exclude(user=self.request.user)

        # 사용자가 선택한 전문분야 토픽
        topic_expertise = user.topic_expertise.all()
        topic_interests = user.topic_interests.all()

        topics = topic_expertise | topic_interests

        # Get Follower's Answers
        following_users = user.following.values_list(flat=True)

        # Filter Answer, order by the most recently modified post
        queryset = queryset & Question.objects.filter(topic__in=topics) \
            .filter(user__in=following_users) \
            .order_by('modified_at')

        if not queryset:
            queryset = Question.objects.all()

        return queryset


class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return QuestionUpdateDestroySerializer
        return QuestionGetSerializer
