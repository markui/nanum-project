from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

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
        error = None

        # 만약 query parameter가 왔는데 value가 오지 않았을 경우
        if "" in list(values):
            error = {"error": "query parameter가 존재하나 value가 존재하지 않습니다."}
        if query_params and not query_params <= filter_fields:
            error = {"error": "존재하지 않는 query_parameter입니다. "
                              "필터가 가능한 query_parameter는 다음과 같습니다:"
                              f"{filter_fields}"}
        if error:
            raise NotFound(detail=error)

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
        error = None

        # 만약 query parameter가 왔는데 value가 오지 않았을 경우
        if "" in list(values):
            error = {"error": "query parameter가 존재하나 value가 존재하지 않습니다."}
        if query_params and not query_params <= filter_fields:
            error = {"error": "존재하지 않는 query_parameter입니다. "
                              "필터가 가능한 query_parameter는 다음과 같습니다:"
                              f"{filter_fields}"}
        if error:
            raise NotFound(detail=error)

        return super().filter_queryset(queryset)

        # def retrieve(self, request, *args, **kwargs):
        #     """
        #     Query parameter에 따라 nested된 filter/pagnating queryset을 추가
        #     :param request:
        #     :param args:
        #     :param kwargs:
        #     :return:
        #     """
        #     query_params = self.request.query_params
        #
        #     immediate_children, all_children = query_params.get('immediate_children'), \
        #                                        query_params.get('all_children')
        #     instance = self.get_object()
        #     parent_serializer = self.get_serializer(instance)
        #
        #     if immediate_children:
        #         queryset = self.filter_queryset(instance.immediate_children)
        #         page = self.paginate_queryset(queryset)
        #     elif all_children:
        #         queryset = self.filter_queryset(instance.all_children)
        #         page = self.paginate_queryset(queryset)
        #     else:
        #         page = None
        #
        #     if page is not None:
        #         children_serializer = self.get_serializer(page, many=True)
        #         paginated_response = self.get_paginated_response(children_serializer.data)
        #         data = OrderedDict(chain(parent_serializer.data.items(), paginated_response.data.items()))
        #         return Response(data)
        #
        #     return Response(parent_serializer.data)
