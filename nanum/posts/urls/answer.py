from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^$', apis.AnswerListCreateView.as_view(), name='list'),
    url(r'(?P<pk>\d+)/$', apis.AnswerRetrieveUpdateDestroyView.as_view(), name='detail'),
    url(r'^main_feed/$', apis.AnswerMainFeedListView.as_view(), name='main_feed'),
    url(r'^bookmark_feed/$', apis.AnswerBookmarkFeedListView.as_view(), name='bookmark_feed'),
    url(r'^filter_feed/$', apis.AnswerFilterFeedListView.as_view(), name='filter_feed'),
]
