from django.conf.urls import url

from . import apis

urlpatterns = [
    url(r'^$', apis.TopicListCreateView.as_view(), name='topic-list'),
    url(r'^(?P<pk>\d+)/$', apis.TopicRetrieveUpdateDestroyView.as_view(), name='topic-detail'),
    url(r'^merge/(?P<pk>\d+)/', apis.TopicMergeView.as_view(), name='topic-merge'),
]