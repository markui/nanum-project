from rest_framework import generics, permissions
from rest_framework.response import Response

from ..serializers.answer import AnswerSerializer
from ..models import Answer

__all__ = (
    'AnswerListCreateView',
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

    def list(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AnswerFeedListView(generics.ListAPIView):
    queryset = Answer
    serializer_class = AnswerSerializer

    def list(self, request, *args, **kwargs):

        pass