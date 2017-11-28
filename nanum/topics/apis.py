from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .serializers import TopicSerializer
from .models import Topic


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000



class TopicList(generics.ListCreateAPIView):
    """
    토픽 전체 API View
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class TopicDetail(generics.RetrieveDestroyAPIView):
    """
    토픽 한개 API View

    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


