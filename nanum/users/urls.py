from django.conf.urls import url

from .apis import SignupView, LoginView, FacebookLoginView, InterestFollowRelationCreateView, \
    ExpertiseFollowRelationCreateView

urlpatterns = [
    # /user/signup/
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    # /user/signup/verify-email/
    # url(r'^signup/verify-email/$', VerfiyEmailView.as_view(), name='verify_email'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    # /user/facebook-login/
    url(r'^facebook-login/$', FacebookLoginView.as_view(), name='facebook-login'),

    # /user/topic-interest-follow-relation/
    url(r'^topic-interest-follow-relation/$', InterestFollowRelationCreateView.as_view(),
        name='topic-interest-follow-relation'),
    url(r'^topic-expertise-follow-relation/$', ExpertiseFollowRelationCreateView.as_view(),
        name='topic-expertise-follow-relation')
]
