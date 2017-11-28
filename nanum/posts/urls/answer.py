from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^user/$', apis.AnswerListCreateView.as_view(), name='user'),
    url(r'^main_feed/$', apis.AnswerMainFeedListView.as_view(), name='main_feed'),
    url(r'^bookmark/$', apis.AnswerBookmarkFeedListView.as_view(), name='bookmark'),
    url(r'^filter/$', apis.AnswerFilterFeedListView.as_view(), name='filter'),
]
