from rest_framework import generics, permissions

from ..models import Comment
from ..serializers import CommentSerializer

__all__ = (
    'CommentListCreateView',
    'CommentRetrieveUpdateDestroyView',
)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        """
        generics의 get_queryset 함수 override
        Comment 중 User가 단 comment queryset 역참조하여 반환
        :return:
        """
        user = self.request.user
        return user.comment_set.all()


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
