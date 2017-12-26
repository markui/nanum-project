from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

# post:question:<name>
urlpatterns = [
    url(r'^$', apis.QuestionListCreateView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', apis.QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),
    url(r'^main_feed/$', apis.QuestionMainFeedListView.as_view(), name='main-feed'),
    # expertise topics filter
    url(r'^filter/$', apis.QuestionFilterListView.as_view(), name='topics-filter'),
]