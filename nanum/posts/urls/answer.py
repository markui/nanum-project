from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^$', apis.AnswerListCreateView.as_view(), name='list_create'),
    url(r'(?P<pk>\d+)/$', apis.AnswerRetrieveUpdateDestroyView.as_view(), name='retrieve_update_destroy'),
    url(r'^main_feed/$', apis.AnswerMainFeedListView.as_view(), name='list_main_feed'),
]
