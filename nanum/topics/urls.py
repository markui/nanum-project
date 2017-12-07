from django.conf.urls import url

from . import apis

urlpatterns = [
    url(r'^$', apis.TopicListCreateView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', apis.TopicDetailView.as_view(), name='detail'),
]