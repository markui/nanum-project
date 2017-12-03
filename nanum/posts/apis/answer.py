import json

from django.http import Http404
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response

import topics
from topics.models import Topic
from ..models import Answer
from ..serializers.answer import AnswerSerializer, AnswerFeedSerializer, AnswerUpdateSerializer
from ..utils import QuillJSImageProcessor

__all__ = (
    'AnswerListCreateView',
    'AnswerRetrieveUpdateDestroyView',
    'AnswerMainFeedListView',
)

img_processor = QuillJSImageProcessor()


class AnswerFilter(filters.FilterSet):
    """
    답변 query_params를 통한 각종 필드 filter를 만들어주는 class
    """
    topic = filters.CharFilter(method='filter_topic')
    bookmarked = filters.CharFilter(method='filter_bookmarked')
    ordering = filters.CharFilter(method='filter_ordering')

    def filter_topic(self, queryset, name, value):
        try:
            value = int(value)
            if not Topic.objects.filter(pk=value).exists():
                return {"message": "해당 value에 대한 Topic이 존재하지 않습니다."}
            return queryset.filter(question__topic=value)
        except ValueError:
            return {"message": "int형태의 값이 아닙니다."}

    def filter_bookmarked(self, queryset, name, value):
        if value == "True":
            filtered_queryset = queryset.filter(answerbookmarkrelation__user=self.request.user)
            return filtered_queryset
        else:
            return {"message": "True만 value로 올 수 있습니다."}

    def filter_ordering(self, queryset, name, value):
        fields = [field.name for field in queryset.model._meta.get_fields()]
        if value in fields:
            return queryset.order_by(value)
        else:
            return {"message": f"value로 전달된 값이 queryset의 필드에 존재하지 않습니다."
                               f"queryset {queryset.model} 은 다음과 같은 필드를 갖고 있습니다: {fields}"}

    class Meta:
        model = Answer
        fields = ['user', 'topic', 'bookmarked', 'ordering']


class AnswerListCreateView(generics.ListCreateAPIView):
    """
    유저가 작성한 Answer들을 갖고와주는 ListCreate API
    """
    queryset = Answer.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AnswerFilter

    def filter_queryset(self, queryset):
        """
        generics의 filter_queryset override

        필터가 가능한 queryset이면 필터를 실시, 그 외의 경우에는 에러 메세지를 반환
        :param queryset: View의 queryset
        """
        query_params = self.request.query_params.keys()
        filter_fields = self.filter_class.get_fields().keys()

        # query_params가 존재하며 filter_fields의 subset 이 아닐 경우
        if query_params and not query_params <= filter_fields:
            result = {"message":"존재하지 않는 query_parameter입니다. 필터가 가능한 query_parameter는 다음과 같습니다:"
                              f"{filter_fields}"}
        else:
            for backend in list(self.filter_backends):
                result = backend().filter_queryset(self.request, queryset, self)

        return result

    def list(self, request, *args, **kwargs):
        """
        ListModelMixin의 list override

        변경점
        1. queryset -> result
        2. Response 에 대한 try except문 추가
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        result = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(result, many=True)
        try:
            return Response(serializer.data)
        except:
            return Response(result, status.HTTP_400_BAD_REQUEST)

    def get_serializer(self, *args, **kwargs):
        """
        Override get_serializer 함수 - POST요청과 GET요청을 나누어 Serializer 종류를 변경
        :param args:
        :param kwargs:
        :return:
        """
        if self.request.method == 'POST':
            serializer_class = AnswerSerializer
        else:
            serializer_class = AnswerFeedSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnswerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Answer 객체 하나를 Retrieve, Update혹은 Destroy 해주는 API
    """
    queryset = Answer.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_serializer(self, *args, **kwargs):
        """
        Override get_serializer 함수 - POST요청과 GET요청을 나누어 Serializer 종류를 변경
        :param args:
        :param kwargs:
        :return:
        """
        if self.request.method == 'POST':
            serializer_class = AnswerUpdateSerializer
        else:
            serializer_class = AnswerSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        instance = self.get_object()
        self.remove_images(instance=instance, request=request)

        # serializer = self.get_serializer(instance, data=request.data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        #
        # if getattr(instance, '_prefetched_objects_cache', None):
        #     # If 'prefetch_related' has been applied to a queryset, we need to
        #     # forcibly invalidate the prefetch cache on the instance.
        #     instance._prefetched_objects_cache = {}
        #
        # return Response(serializer.data)

    def remove_images(self, instance, request):
        """
        instance_delta에는 있는데 request_delta에는 없는 image들을 storage에서 삭제하는 함수를 호출
        :param instance:
        :param request:
        :return:
        """
        instance_delta = instance.content
        instance_image_list = self.get_image_list(instance_delta)
        instance_image_set = set(instance_image_list)

        self.modify_request_data(request)
        request_delta = img_processor.get_delta(request.data.get('content'))
        request_image_list = self.get_image_list(request_delta)
        request_image_set = set(request_image_list)

        to_be_deleted = list(instance_image_set - request_image_set)

    def get_image_list(self, delta):
        """
        Dict형태의 quillJS delta 값을 받아 delta안에 image의 url들을 추출해 List형태로 반환
        :param content: dict 형태의 quillJS content
        :return:
        """
        delta_list = img_processor.get_delta_list(delta=delta, iterator=True)
        image_url_list = list()
        for item in delta_list:
            try:
                image_url = item['insert']['image']
                image_url_list.append(image_url)
            except:
                continue
        return image_url_list

    def modify_request_data(self, request):
        """
        request를 parameter로 받아 content내용을 변화시킴

        :param request: Django Request 객체
        :return:
        """
        request.data._mutable = True
        content, question = request.data.get('content'), request.data.get('question')
        if content:
            request.data['content'] = self.modify_content_image_value(content=content, question=question)
        request.data._mutable = False

    def modify_content_image_value(self, content, question, *args, **kwargs):
        """
        Content의 image key의 value들을 base64형태의 전체 파일에서
        storage의 url(local일 경우 default storage, deploy일 경우 S3)로 변환하여 새 content 반환

        :param content: request객체에서 꺼낸 content dictionary
        :param question: 해당 답변이 쓰이는 question 객체
        :param args:
        :param kwargs:
        :return: modified_content: "image" key 의 value가 url로 바뀐 content
        """
        # Initializer quillJSImageProcessor
        delta = img_processor.get_delta(content=content)
        delta_list = img_processor.get_delta_list(delta=delta)

        # iterate through delta list to modify the image string
        for item in delta_list:
            url = img_processor.get_image_url(item=item, question=question)
            if url:  # 반환된 값이 url일 경우
                item['insert']['image'] = url

        modified_content = json.dumps(delta)
        return modified_content

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class AnswerMainFeedListView(generics.ListAPIView):
    """
    유저를 위한 주 답변 Feed
    1. Topic, Follower를 기반으로 개인화된 피드 생성
    2. +추후 Like 정보 추가
    3. +추후 CF Filtering / Content-based Filtering 적용
    """
    serializer_class = AnswerFeedSerializer

    def get_queryset(self):
        """
        Topic, Follower 기반 filter된 queryset 반환
        :return:
        """
        user = self.request.user

        # Get all Topics that user is following
        answer_topic_interest = list(user.topic_interests.values_list(flat=True))
        answer_topic_expertise = list(user.topic_expertise.values_list(flat=True))

        # Combine both
        answer_topic = answer_topic_interest.extend(answer_topic_expertise)

        # Get Follower's Answers
        following_users = user.following.values_list(flat=True)

        # Filter Answer, order by the most recently modified post
        queryset = Answer.objects.filter(topic__in=answer_topic) \
            .filter(user__in=following_users) \
            .order_by('modified_at')

        return queryset
