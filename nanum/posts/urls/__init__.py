from django.conf.urls import url, include
from .comment import *
from .question import *

urlpatterns = [
    url(r'^comment/', include('posts.urls.comment')),
    url(r'^question/', include('posts.urls.question')),
]