from django.conf.urls import url

from users.apis.relation.follow import UserFollowRelationCreateView, UserFollowRelationDetailView, \
    QuestionFollowRelationCreateView, QuestionFollowRelationDetailView
from .apis import SignupView, LoginView, FacebookLoginView, InterestFollowRelationCreateView, \
    ExpertiseFollowRelationCreateView, InterestFollowRelationDetailView, ExpertiseFollowRelationDetailView

urlpatterns = [
    # AUTH

    # /user/signup/
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    # /user/signup/verify-email/
    # url(r'^signup/verify-email/$', VerfiyEmailView.as_view(), name='verify_email'),
    url(r'^login/$', LoginView.as_view(), name='login'),

    # SOCIAL_AUTH

    # /user/facebook-login/
    url(r'^facebook-login/$', FacebookLoginView.as_view(), name='facebook-login'),

    # RELATION
    # 1. FOLLOW

    # 1-1. FOLLOW-TOPIC

    # /user/topic-interest-follow-relation/
    url(r'^topic-interest-follow-relation/$', InterestFollowRelationCreateView.as_view(),
        name='topic-interest-follow-relation'),
    # /user/topic-interest-follow-relation/1/
    url(r'^topic-interest-follow-relation/(?P<pk>\d+)/$', InterestFollowRelationDetailView.as_view(),
        name='topic-interest-follow-relation-detail'),
    # /user/topic-expertise-follow-relation/
    url(r'^topic-expertise-follow-relation/$', ExpertiseFollowRelationCreateView.as_view(),
        name='topic-expertise-follow-relation'),
    # /user/topic-expertise-follow-relation/1/
    url(r'^topic-expertise-follow-relation/(?P<pk>\d+)/$', ExpertiseFollowRelationDetailView.as_view(),
        name='topic-expertise-follow-relation-detail'),

    # 1-2. FOLLOW-USER

    # /user/user-follow-relation/
    url(r'^user-follow-relation/$', UserFollowRelationCreateView.as_view(),
        name='user-follow-relation'),
    # # /user/user-follow-relation/1/
    url(r'^user-follow-relation/(?P<pk>\d+)/$', UserFollowRelationDetailView.as_view(),
        name='user-follow-relation-detail'),

    # 1-3. FOLLOW-QUESTION

    # /user/question-follow-relation/
    url(r'^question-follow-relation/$', QuestionFollowRelationCreateView.as_view(),
        name='question-follow-relation'),
    # /user/question-follow-relation/1/
    url(r'^question-follow-relation/(?P<pk>\d+)/$', QuestionFollowRelationDetailView.as_view(),
        name='question-follow-relation-detail'),
]
