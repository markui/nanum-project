from __future__ import unicode_literals
from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

__all__ = (
    'CommentPagination',
)


class CustomPagination(PageNumberPagination):
    """
    Custom Pagination Class
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListPagination(CustomPagination):
    """

    """
    pass


class CommentPagination(CustomPagination):
    def get_paginated_response(self, data):
        """
        추후 immediate_children count에 대한 처리 논의
        :param data:
        :return:
        """
        immediate_children = self.request.query_params.get('immediate_children')
        if immediate_children:
            return Response(OrderedDict([
                ('immediate_cihldren_count', self.page.paginator.count),
                ('results', data),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link())
            ]))
        return Response(OrderedDict([
            ('results', data),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link())
        ]))
