import django_filters
from django_filters import rest_framework as filters, OrderingFilter
from django_filters.fields import Lookup
from rest_framework.exceptions import ParseError

from ..models import Answer, Question, Comment

__all__ = (
    'AnswerFilter',
    'QuestionFilter',
)


class ListFilter(django_filters.Filter):
    """
    List 형태로 query가 오는 것을 or 연산으로 필터 가능하게 해주는 필터
    """

    def sanitize(self, value_list):
        """
        /?<query_param>=<v1>,<v2>,<v3> 로 온 v1,v2,v3 등의 value값을 list로 변환,
        만약 값이 비어있을 시 list에서 제외
        """
        return [v for v in value_list if v != u'']

    def customize(self, value):
        return value

    def filter(self, qs, value):
        multiple_vals = value.split(u",")
        multiple_vals = self.sanitize(multiple_vals)
        multiple_vals = map(self.customize, multiple_vals)
        return super().filter(qs, Lookup(multiple_vals, 'in'))


class IntegerListFilter(ListFilter):
    def customize(self, value):
        try:
            return int(value)
        except:
            raise ParseError({"error": "이 query_parameter에 해당하지 않는 type의 value입니다"})


class AnswerFilter(filters.FilterSet):
    """
    답변 query_params를 통한 각종 필드 filter를 만들어주는 class
    """
    user = IntegerListFilter(name='user', )
    topic = IntegerListFilter(name='question__topics')
    bookmarked_by = IntegerListFilter(name='answerbookmarkrelation__user', )
    ordering = OrderingFilter(
        fields=(
            ('modified_at', 'modified_at'),
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Answer
        fields = ['user', 'topic', 'bookmarked_by', ]


class CommentFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ('modified_at', 'modified_at'),
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Comment
        fields = []


class CommentListFilter(CommentFilter):
    question = ListFilter(name='comment_post_intermediate__question')
    answer = ListFilter(name='comment_post_intermediate__answer')

    class Meta:
        model = Comment
        fields = ['question', 'answer']


# QuestionListFilter
class QuestionListFilter(django_filters.Filter):
    def filter(self, qs, value):
        return super().filter(qs, Lookup(value, 'in'))


class QuestionFilter(django_filters.FilterSet):
    # 해당 유저의 모든 질문
    user = QuestionListFilter(name='user', )
    # 해당 유저가 답변한 질문
    answered_by = QuestionListFilter(name='answer__user_id', )
    # 해당 유저가 팔로우하는 질문
    followed_by = QuestionListFilter(name='followers', )
    # 해당 유저가 북마크하는 질문
    bookmarked_by = QuestionListFilter(name='who_bookmarked', )
    # 해당 topic을 포함하는 질문
    topic = QuestionListFilter(name='topics', )
    ordering = OrderingFilter(
        fields=(
            ('modified_at', 'modified_at'),
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Question
        fields = ['user', 'answered_by', 'bookmarked_by', 'followed_by', 'topic']
