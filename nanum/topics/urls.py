from django.conf.urls import url

from . import apis

urlpatterns = [
    url(r'^$', apis.TopicListCreateView.as_view(), name='list_create'),
    url(r'^(?P<pk>\d+)/$', apis.TopicRetrieveUpdateDestroyView.as_view(), name='retrieve_update_destroy'),
]