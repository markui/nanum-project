from django.conf.urls import url

from .apis import SignupView, LoginView, FacebookLoginView

urlpatterns = [
    # /user/signup/
    url(r'^signup/$', SignupView.as_view(), name='signup'),
# /user/signup/verify-email/
    # url(r'^signup/verify-email/$', VerfiyEmailView.as_view(), name='verify_email'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    # /user/facebook-login/
    url(r'^facebook-login/$', FacebookLoginView.as_view(), name='facebook-login'),


]
