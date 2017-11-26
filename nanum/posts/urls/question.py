from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    url(r'^$', apis.QuestionAPI.as_view(), name='question'),
]