from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^$', apis.CommentListCreateView.as_view(), name='list_create'),
    url(r'^(?P<pk>\d+)/$', apis.CommentRetrieveUpdateDestroyView.as_view(), name='retrieve_update_destroy'),
]
