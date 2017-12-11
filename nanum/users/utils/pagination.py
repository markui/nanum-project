from rest_framework.pagination import (
    PageNumberPagination,
)

__all__ = (
    'UserFollowParticipantPagination',
    'FollowingTopicPagination',
)


class UserFollowParticipantPagination(PageNumberPagination):
    """
    팔로워 또는 팔로우 List에 대한 Pagination Class
    """
    page_size = 10
    page_size_query_param = 'page_size'


class FollowingTopicPagination(PageNumberPagination):
    """
    팔로우 하는 Topic에 대한 Pagination Class
    """
    page_size = 4
    page_size_query_param = 'page_size'
