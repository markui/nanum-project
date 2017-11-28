from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import generics, permissions
from rest_framework.response import Response

from ..serializers.answer import AnswerSerializer, AnswerFeedSerializer
from ..models import Answer

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
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        user = self.request.user
        return user.answer_set.all()

class AnswerMainFeedListView(generics.ListAPIView):
    queryset = Answer
    serializer_class = AnswerFeedSerializer

    def list(self, request, *args, **kwargs):

        pass

class AnswerBookmarkFeedListView(generics.ListAPIView):
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

