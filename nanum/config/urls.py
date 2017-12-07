from django.conf.urls import url, include
from django.contrib import admin
# test
from django.conf.urls.static import static
from django.conf import settings
from . import views
from rest_framework.authtoken import views as rest_views

urlpatterns = [
    # test
    url(r'^$', views.index),

    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('users.urls', namespace='user')),
    url(r'^post/', include('posts.urls', namespace='post')),
    url(r'^topic/', include('topics.urls', namespace='topic')),
    url(r'^api-token-auth/', rest_views.obtain_auth_token),
]

# test
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
