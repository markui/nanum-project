from django.conf.urls import url, include

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^$', apis.AnswerListCreateView.as_view(), name='answer'),
]