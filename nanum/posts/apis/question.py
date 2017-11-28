from rest_framework import generics

from posts.models import Question
from ..serializers.question import QuestionSerializer

__all__ = (
    'QuestionAPI',
)


class QuestionAPI(generics.CreateAPIView):
    queryset = Question
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
