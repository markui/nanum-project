from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from users.models import AnswerUpVoteRelation
from users.utils.permissions import IsUserWhoTookAction
from ...serializers import AnswerVoteRelationSerializer


class AnswerUpVoteRelationCreateView(generics.CreateAPIView):
    """
    유저 - 답변 추천 관계 생성
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AnswerVoteRelationSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        오버라이드를 하여 serializer에게 "추천" type이라는 정보를 전달
        """
        context = super().get_serializer_context()
        context.update({'vote_type': 'upvote'})
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnswerUpVoteRelationDetailView(generics.RetrieveDestroyAPIView):
    """
        유저 - 유저 팔로우 관계 가져오기 / 삭제하기
        """
    permission_classes = (
        IsAuthenticated,
        IsUserWhoTookAction,
    )

    queryset = AnswerUpVoteRelation.objects.all()


class AnswerDownVoteRelationCreateView(generics.CreateAPIView):
    """
    유저 - 답변 비추천 관계 생성
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AnswerVoteRelationSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        오버라이드를 하여 serializer에게 "비추천" type이라는 정보를 전달
        """
        context = super().get_serializer_context()
        context.update({'vote_type': 'downvote'})
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
