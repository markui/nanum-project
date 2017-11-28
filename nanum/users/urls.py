from django.conf.urls import url

from .apis import SignupView, LoginView

urlpatterns = [
    # /user/signup/
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^login/$', LoginView.as_view(), name='login'),

    # /user/signup/verify-email/
    # url(r'^signup/verify-email/$', VerfiyEmailView.as_view(), name='verify_email'),
]
