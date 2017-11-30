from rest_framework import generics

from posts.models import Question
from ..serializers.question import QuestionSerializer

__all__ = (
    'QuestionListCreateView',
)


class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    # permission_classes = ()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.filter()
    serializer_class = QuestionSerializer
