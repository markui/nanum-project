from django.conf.urls import url

from . import apis

urlpatterns = [
    url(r'^$', apis.TopicList.as_view(), name='topic-list'),
    url(r'^(?P<pk>\d+)/$', apis.TopicDetail.as_view(), name='topic-detail'),
]