from collections import OrderedDict
from itertools import chain

from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from posts.serializers.comment import CommentUpdateSerializer
from posts.utils.filters import CommentFilter
from ..models import Comment
from ..serializers import CommentGetSerializer, CommentCreateSerializer
from ..utils.pagination import CustomPagination, CommentPagination
from ..utils.permissions import IsAuthorOrAuthenticatedReadOnly

__all__ = (
    'CommentListCreateView',
    'CommentRetrieveUpdateDestroyView',
)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Comment List, Create API View
    Comment가 달린 Answer 혹은 Question의 정보를 string 포맷으로 반환 - "<post_type> - <post_pk>" 형식으로 표현
    """
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    pagination_class = CustomPagination

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            serializer_class = CommentCreateSerializer
        else:
            serializer_class = CommentGetSerializer

        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        """
        generics의 get_queryset 함수 override
        Comment 중 User가 단 comment queryset 역참조하여 반환
        :return:
        """
        user = self.request.user
        return user.comment_set.all()


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Comment Retrieve, Update, Destroy API View
    Author 일 경우 Update, Destroy가 가능하고 Authenticated 일 경우 Get이 가능
    """
    queryset = Comment.objects.all()
    permission_classes = (
        IsAuthorOrAuthenticatedReadOnly,
    )
    pagination_class = CommentPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CommentFilter  # utils.filter

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
            error = {"message": "query parameter가 존재하나 value가 존재하지 않습니다."}
        if query_params and not query_params <= filter_fields:
            error = {"message": "존재하지 않는 query_parameter입니다. "
                                "필터가 가능한 query_parameter는 다음과 같습니다:"
                                f"{filter_fields}"}
        if error:
            raise NotFound(detail=error)

        return super().filter_queryset(queryset)

    def get_serializer(self, *args, **kwargs):
        """
        GenericAPIView get_serializer override
        PUT, PATCH와 GET요청을 나누어 Serializer 종류를 변경
        GET 요청 중 query parameter에 immediate_children = True 혹은 all_children =True가 올 경우
            해당 information을 담아서 보내주는 Serializer를 serializer_class로 설정
        :param args:
        :param kwargs:
        :return:
        """
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = CommentUpdateSerializer
        else:
            serializer_class = CommentGetSerializer

        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        query_params = self.request.query_params
        immediate_children, all_children = query_params.get('immediate_children'), \
                                           query_params.get('all_children')
        instance = self.get_object()
        parent_serializer = self.get_serializer(instance)

        if immediate_children:
            queryset = self.filter_queryset(instance.immediate_children)
            page = self.paginate_queryset(queryset)
        elif all_children:
            queryset = self.filter_queryset(instance.all_children)
            page = self.paginate_queryset(queryset)
        else:
            page = None

        if page is not None:
            children_serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(children_serializer.data)
            data = OrderedDict(chain(parent_serializer.data.items(), paginated_response.data.items()))
            return Response(data)

        return Response(parent_serializer.data)
