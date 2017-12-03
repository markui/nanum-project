from rest_framework import generics, permissions

from posts.models import Question
from ..serializers.question import QuestionSerializer

__all__ = (
    'QuestionListCreateView',
    'QuestionRetrieveUpdateDestroyView',
)


#########################################
# 1. 전문분야 질문 리스트(질문 읽기 페이지 메인) [X]
# 2. 북마크한 질문 리스트 [X]
# 3. 최신 질문 리스트 [X]
# 4. 나에게 요청된 질문 리스트 []
# 5. 답변 중인 질문 리스트 []
#########################################

# 전문분야 질문리스트
class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        exclude_user = Question.objects.exclude(user=self.request.user)
        query_set = Question.objects.none()

        # 사용자가 선택한 전문분야 토픽
        topics = self.request.user.topic_expertise.all()
        # query-set(자기가 쓴 글 제외, 선택한 전문분야의 글 모두 취합)
        for topic in topics:
            query_set = exclude_user & Question.objects.filter(topics=topic.id) | query_set

        return query_set

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# detail
class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )


# 내가 북마크 한 질문리스트
class BookMarkedQuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        query_set = Question.objects.none()
        bookmarked_questions = self.request.user.bookmarked_questions.all()

        for question in bookmarked_questions:
            query_set = Question.objects.get(id=question.id) | query_set

        return query_set
