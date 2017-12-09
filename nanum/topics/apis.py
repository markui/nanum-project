from rest_framework import generics, permissions

from .models import Topic
from .serializers import TopicSerializer
from .utils.pagination import ListPagination
from .utils.permissions import IsStaffOrAuthenticatedReadOnly


class TopicListCreateView(generics.ListCreateAPIView):
    """
    Topic ListAPIView 와
    Topic CreateAPIView


    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    pagination_class = ListPagination

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TopicRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Topic RetrieveAPIView
    Topic UpdateAPIView
    Topic Destroy APIView

    Retrieve의 경우 authenticated면 볼 수 있으며,
    Update(PUT, PATCH)와 Destroy의 경우 Staff 일 경우에만 가능
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (
        IsStaffOrAuthenticatedReadOnly,
    )


class TopicMergeView(generics.CreateAPIView):
    """

    """
    pass
