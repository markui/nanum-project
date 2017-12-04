from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    # posts:question:
    url(r'^$', apis.QuestionListCreateView.as_view(), name='question-list'),
    url(r'^(?P<pk>\d+)/$', apis.QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),
    url(r'^bookmarked-question/$', apis.BookMarkedQuestionListView.as_view(), name='bookmarked-question'),
]