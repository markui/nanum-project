from rest_framework import generics, permissions
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from topics.models import Topic
from topics.serializers import TopicSerializer
from . import search


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


class SearchAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        query_params = self.request.query_params
        query = query_params.get("query", None)
        if not query:
            raise ParseError({"error": "query 필드가 비어있습니다."})
        result = search.search(query)
        return Response(result)
