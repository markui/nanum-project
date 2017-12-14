from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^$', apis.AnswerListCreateView.as_view(), name='answer-list'),
    url(r'(?P<pk>\d+)/$', apis.AnswerRetrieveUpdateDestroyView.as_view(), name='answer-detail'),
    url(r'^main_feed/$', apis.AnswerMainFeedListView.as_view(), name='answer-main'),
    # url('^filter_list/$', apis.AnswerFeedFilterView.as_view(), name='answer-filterlist'),
]
