from rest_framework import generics, permissions

from posts.models import Question
from ..serializers.question import QuestionSerializer

__all__ = (
    'QuestionListCreateView',
)


#####################################
# 1. 전문분야 질문 리스트(질문 읽기 페이지 메인)
# 2. 북마크한 질문 리스트
# 3. 최신 질문 리스트
# 4. 나에게 요청된 질문 리스트
# 5. 답변 중인 질문 리스트
######################################

# 전문분야 질문리스트
class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        topic_list = list()
        # 사용자가 선택한 전문분야 토픽
        topics = self.request.user.topic_expertise.all()
        # query-set
        for topic in topics:
            topic_list.append(topic.id)
        return Question.objects.exclude(user=self.request.user) & \
               Question.objects.filter(topic_id=topic_list[0]) | \
               Question.objects.filter(topic_id=topic_list[1]) | \
               Question.objects.filter(topic_id=topic_list[2])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
