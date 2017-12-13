from rest_framework import generics, permissions
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from topics.models import Topic
from topics.serializers import TopicSerializer


class TopicSearchAPIView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    authentication_classes = (
        permissions.IsAuthenticated,
    )

    def retrieve(self, request, *args, **kwargs):
        query_params = self.request.query_params
        topic_name = query_params.get("name", None)
        if not topic_name:
            raise ParseError(detail={"error": "name 필드가 비어있습니다."})

        queryset = Topic.objects.filter(name__contains=topic_name)

        if not queryset:
            return Response({"result": "결과가 없습니다."})

        serializer = self.get_serializer(queryset, many=True)
        result = {"result": serializer.data}
        return Response(result)
