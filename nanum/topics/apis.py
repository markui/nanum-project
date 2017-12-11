from collections import OrderedDict

from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .models import Topic
from .serializers import TopicSerializer, TopicGetSerializer
from .utils.pagination import ListPagination
from .utils.permissions import IsAdminUserOrAuthenticatedReadOnly


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
        IsAdminUserOrAuthenticatedReadOnly,
    )


class TopicMergeView(generics.GenericAPIView):
    """
    Topic 1 = from
    Topic 2 = to
    """
    queryset = Topic.objects.all()
    serializer_class = TopicGetSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # get pk
        to_pk = request.data.get('topic_to')
        if not to_pk:
            raise ParseError(detail={"error": "topic_to 필드가 비어있습니다."})
        try:
            to_pk = int(to_pk)
        except ValueError:
            raise ParseError(detail={"error": "topic_to 필드가 Integer로 변환가능한 필드가 아닙니다."})

        # get object
        topic_from_instance = self.get_object()
        topic_to_instance = get_object_or_404(Topic, pk=to_pk)

        serializer_from = {"from": self.get_serializer(topic_from_instance).data}
        serializer_to = {"to": self.get_serializer(topic_to_instance).data}

        # Merge
        instance = self.merge_instances(from_instance=topic_from_instance, to_instance=topic_to_instance)
        serializer = {"result": self.get_serializer(instance).data}

        result = OrderedDict(**serializer_from, **serializer_to, **serializer)
        return Response(result)

    @atomic
    def merge_instances(self, from_instance, to_instance):
        """
        from_instance와 연결된 모든 related instance 들에 대해 정보를 to_instance로 변경
        count 정보 update

        :param from_instance:
        :param to_instance:
        :return:
        """
        assert type(from_instance) == type(to_instance)

        # Topic과 연결되어 있는 mtm(Through field로 지정되어 있는 필드는 제외한), mto 필드들을 갖고 옴
        relation_fields = [
            field for field in from_instance._meta.get_fields()
            if field.one_to_many or (field.many_to_many and field.through._meta.auto_created)
        ]
        self._merge(relation_fields=relation_fields, from_instance=from_instance, to_instance=to_instance)
        from_instance.recount()
        to_instance.recount()

        return to_instance

    @atomic
    def _merge(self, relation_fields, from_instance, to_instance):
        """
        topic.<mtm / mto 필드>.all()을 실행하여 queryset이 존재할 경우
        queryset 안의 instance들에 대햐여
        그 instance들의 topic을 from_instance에서 to_instance로 변경

        예를 들어,
        merge 하는 토픽(없어지는) : topic1 = Topic.objects.first()
        merge 당하는 토픽(추가되는 : topic2 = Topic.objects.last()
        topic1.questions.all() 에 있는 question_instance 들에 대해
        question_instance.topics.add(topic2)
        question_instance.topics.remove(topic1)
        :param relation_fields:
        :param from_instance:
        :param to_instance:
        :return:
        """
        for field in relation_fields:
            field_name = field.get_accessor_name() or field.name
            reverse_field_name = field.field.name
            queryset = getattr(from_instance, field_name).all().iterator()
            if queryset:
                for rel_instance in queryset:
                    try:
                        getattr(rel_instance, reverse_field_name).add(to_instance)
                        getattr(rel_instance, reverse_field_name).remove(from_instance)
                    except:
                        setattr(rel_instance, reverse_field_name, to_instance)
