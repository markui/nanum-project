from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, ParseError

from utils.permissions import IsAuthorOrAuthenticatedReadOnly
from ..models import Comment
from ..serializers import CommentSerializer, CommentCreateSerializer
from ..utils.filters import CommentFilter, CommentListFilter
from ..utils.pagination import CommentPagination, ListPagination

__all__ = (
    'CommentListCreateView',
    'CommentRetrieveUpdateDestroyView',
)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Comment List, Create API View
    Comment가 달린 Answer 혹은 Question의 정보를 string 포맷으로 반환 - "<post_type> - <post_pk>" 형식으로 표현
    """
    queryset = Comment.objects.filter(parent=None)
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    pagination_class = ListPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CommentListFilter

    def filter_queryset(self, queryset):
        """
        GenericAPIView의 filter_queryset override
        필터가 가능한 queryset이면 필터를 실시, 그 외의 경우에는 에러 메세지를 반환

        :param queryset: View의 queryset
        """
        query_params = self.request.query_params.keys()
        values = self.request.query_params.values()
        filter_fields = self.filter_class.get_fields().keys() | \
                        {'ordering', 'page', 'user', 'question', 'answer'}

        # 만약 query parameter가 왔는데 value가 오지 않았을 경우
        if "" in list(values):
            raise ParseError({"error": "query parameter가 존재하나 value가 존재하지 않습니다."})
        if query_params and not query_params <= filter_fields:
            raise ParseError({"error": "존재하지 않는 query_parameter입니다. "
                              "필터가 가능한 query_parameter는 다음과 같습니다:"
                              f"{filter_fields}"})

        return super().filter_queryset(queryset)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            serializer_class = CommentCreateSerializer
        else:
            serializer_class = CommentSerializer

        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Comment Retrieve, Update, Destroy API View
    Author 일 경우 Update, Destroy가 가능하고 Authenticated 일 경우 Get이 가능
    """
    queryset = Comment.objects.all()
    permission_classes = (
        IsAuthorOrAuthenticatedReadOnly,
    )
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CommentFilter

    def filter_queryset(self, queryset):
        """
        GenericAPIView의 filter_queryset override
        필터가 가능한 queryset이면 필터를 실시, 그 외의 경우에는 에러 메세지를 반환

        :param queryset: View의 queryset
        """
        query_params = self.request.query_params.keys()
        values = self.request.query_params.values()
        filter_fields = self.filter_class.get_fields().keys() | \
                        {'ordering', 'page', 'immediate_children', 'all_children'}

        # 만약 query parameter가 왔는데 value가 오지 않았을 경우
        if "" in list(values):
            raise ParseError({"error": "query parameter가 존재하나 value가 존재하지 않습니다."})
        if query_params and not query_params <= filter_fields:
            raise ParseError({"error": "존재하지 않는 query_parameter입니다. "
                              "필터가 가능한 query_parameter는 다음과 같습니다:"
                              f"{filter_fields}"})

        return super().filter_queryset(queryset)
