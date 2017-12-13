from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    # post:question:
    url(r'^$', apis.QuestionListCreateView.as_view(), name='question-list'),
    url(r'^(?P<pk>\d+)/$', apis.QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),
    url(r'^main_feed/$', apis.QuestionMainFeedListView.as_view(), name='question-main-feed'),
]