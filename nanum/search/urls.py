from django.conf.urls import url

from search import apis

urlpatterns = [
    url(r'^topic/$', apis.TopicSearchAPIView.as_view(), name='topic'),
    url(r'^$', apis.SearchAPIView.as_view(), name='search'),
]