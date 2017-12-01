from django.conf.urls import url

from .. import apis

__all__ = (
    'urlpatterns',
)

urlpatterns = [
    # posts:question:create
    url(r'^$', apis.QuestionListCreateView.as_view(), name='question-create'),
]