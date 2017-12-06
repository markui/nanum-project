from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from posts.models import Question
from posts.utils.filters import QuestionFilter
from ..serializers.question import QuestionSerializer

__all__ = (
    'QuestionListCreateView',
    'QuestionMainFeedListView',
)

User = get_user_model()


class FeedPagination(PageNumberPagination):
    """
    Answer List에 대한 Pagination Class
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100000


#############################################################
# 1. 내 질문을 제외한 전문분야, 관심분야 질문 리스트(main-feed) [X]
# 2. 북마크한 질문 리스트, 최신 질문 리스트 [X]
# 4. 나에게 요청된 질문 리스트 []
# 5. 답변 중인 질문 리스트 []
#############################################################

# 내 질문을 제외한 전문분야, 관심분야 질문 리스트(main-feed)
class QuestionMainFeedListView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        user = self.request.user

        exclude_user = Question.objects.exclude(user=self.request.user)
        query_set = Question.objects.none()

        # 사용자가 선택한 전문분야 토픽
        topic_expertise = user.topic_expertise.value_lists(flat=True)
        topic_interests = user.topic_interests.value_lists(flat=True)

        topics = topic_expertise.extend(topic_interests)

        # Get Follower's Answers
        following_users = user.following.values_list(flat=True)

        # Filter Answer, order by the most recently modified post
        queryset = Question.objects.filter(topic__in=topics) \
            .filter(user__in=following_users) \
            .order_by('modified_at')

        if not queryset:
            queryset = Question.objects.all()

        return queryset


class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = QuestionFilter  # utils.filter

    def filter_queryset(self, queryset):
        """
        GenericAPIView의 filter_queryset override
        필터가 가능한 queryset이면 필터를 실시, 그 외의 경우에는 에러 메세지를 반환

        :param queryset: View의 queryset
        """
        query_params = self.request.query_params.keys()
        values = self.request.query_params.values()
        filter_fields = self.filter_class.get_fields().keys() | {'ordering'}
        error = None

        # 만약 query parameter가 왔는데 value가 오지 않았을 경우
        if "" in list(values):
            error = {"message": "query parameter가 존재하나 value가 존재하지 않습니다."}

        elif query_params and not query_params <= filter_fields:
            error = {"message": "존재하지 않는 query_parameter입니다. "
                                "필터가 가능한 query_parameter는 다음과 같습니다:"
                                f"{filter_fields}"}
        else:
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, self)
        # error가 존재할 경우 list에 error를 전달, 아닐 경우 필터된 queryset이 들어감
        return error, queryset

    def list(self, request, *args, **kwargs):
        """
        ListModelMixin의 list override
        filter_queryset 실행 시 error가 반환되었으면 error를 담은 400 BAD REQUEST를 반환

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        error, queryset = self.filter_queryset(self.get_queryset())
        if error:
            return Response(error, status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    # # 내가 북마크 한 질문리스트
    # class BookMarkedQuestionListView(generics.ListAPIView):
    #     serializer_class = QuestionSerializer
    #     permission_classes = (
    #         permissions.IsAuthenticatedOrReadOnly,
    #     )
    #
    #     def get_queryset(self):
    #         return self.request.user.bookmarked_questions.all()
    #
    #
    # # 최신 질문 리스트
    # class QuestionListView(generics.ListAPIView):
    #     serializer_class = QuestionSerializer
    #
    #     def get_queryset(self):
    #         return Question.objects.exclude(self.request.user)


    ###################################################
    # class MainQuestionListCreateView(generics.ListCreateAPIView):
    #     serializer_class = QuestionSerializer
    #     permission_classes = (
    #         permissions.IsAuthenticated,
    #     )
    #     filter_backends = (filters.DjangoFilterBackend, )
    #     filter_class = QuestionFilter
    #     filter_fields = ('user', 'content', 'topics', )
    #
    #     def get_queryset(self):
    #         queryset = Question.objects.all()
    #
    #         query = self.request.GET.get("q")
    #         print(query)
    #
    #         if query:
    #             queryset = queryset.filter(
    #                 Q(content__icontains=query) |
    #                 Q(user__email__icontains=query)
    #             ).distinct()
    #         return queryset
    #
    #         # bookmarked = self.request.GET.getlist('bookmarked', '')
    #         # if bookmarked:
    #         #     queryset = queryset.filter(name=questionbookmarkrelation__user, )
    #         # queryset = queryset.filter(user=self.request.user)
    #         # return queryset
    ###########################################
