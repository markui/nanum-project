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
    Topic List Pagination
    """
    page_size = 4
