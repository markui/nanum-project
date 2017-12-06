from rest_framework import generics, permissions

from posts.serializers.comment import CommentUpdateSerializer
from ..models import Comment
from ..serializers import CommentSerializer
from ..utils.permissions import IsAuthorOrAuthenticatedReadOnly

__all__ = (
    'CommentListCreateView',
    'CommentRetrieveUpdateDestroyView',
)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Comment List, Create API View
    """
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

class CommentChildrenListView(generics.ListAPIView):
    """
    Comment Children List
    한 코멘트에 대해 밑에 딸려 있는 자식 Comment들을 반환하는 listview
    """
    pass

class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Comment Retrieve, Update, Destroy API View
    Author 일 경우 Update, Destroy가 가능하고 Authenticated 일 경우 Get이 가능
    """
    queryset = Comment.objects.all()
    permission_classes = (
        IsAuthorOrAuthenticatedReadOnly,
    )

    def get_serializer(self, *args, **kwargs):
        """
        GenericAPIView get_serializer override
        PUT, PATCH와 GET요청을 나누어 Serializer 종류를 변경

        :param args:
        :param kwargs:
        :return:
        """
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = CommentUpdateSerializer
        else:
            serializer_class = CommentSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
