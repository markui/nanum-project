import django_filters
from django_filters import rest_framework as filters, OrderingFilter
from django_filters.fields import Lookup

from ..models import Answer, Comment

__all__ = (
    'AnswerFilter',
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


class AnswerFilter(filters.FilterSet):
    """
    답변 query_params를 통한 각종 필드 filter를 만들어주는 class
    """
    user = ListFilter(name='user', )
    topic = ListFilter(name='question__topics')
    bookmarked_by = ListFilter(name='answerbookmarkrelation__user', )
    ordering = OrderingFilter(
        fields=(
            ('modified_at', 'modified_at'),
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Answer
        fields = ['user', 'topic', 'bookmarked_by', ]

class CommentFilter(AnswerFilter):
    ordering = OrderingFilter(
        fields=(
            ('modified_at', 'modified_at'),
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Comment
        fields = []