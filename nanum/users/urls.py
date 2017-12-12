from django.conf.urls import url

from users.apis import ProfileRetrieveUpdateView, EmploymentCredentialListCreateView, EmploymentCredentialDetailView, \
    ProfileStatsRetrieveView, EducationCredentialListCreateView, EducationCredentialDetailView, PasswordResetEmailView
from users.apis.relation.follow import UserFollowRelationCreateView, UserFollowRelationDetailView, \
    QuestionFollowRelationCreateView, QuestionFollowRelationDetailView, UserFollowerListView, UserFollowingListView, \
    FollowingInterestListView, FollowingExpertiseListView
from users.apis.relation.vote import AnswerUpVoteRelationCreateView, AnswerUpVoteRelationDetailView, \
    AnswerDownVoteRelationCreateView
from .apis import SignupView, LoginView, FacebookLoginView, InterestFollowRelationCreateView, \
    ExpertiseFollowRelationCreateView, InterestFollowRelationDetailView, ExpertiseFollowRelationDetailView

urlpatterns = [
    # AUTH

    # /user/signup/
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    # /user/signup/verify-email/
    # url(r'^signup/verify-email/$', VerfiyEmailView.as_view(), name='verify_email'),
    url(r'^login/$', LoginView.as_view(), name='login'),

    url(r'^send-reset-password-email/$', PasswordResetEmailView.as_view(), name='password-reset'),

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
    # /user/1/following-interests/
    url(r'^(?P<pk>\d+)/following-interests/$', FollowingInterestListView.as_view(),
        name='following-interests'),
    # /user/1/following-expertise/
    url(r'^(?P<pk>\d+)/following-expertise/$', FollowingExpertiseListView.as_view(),
        name='following-expertise'),

    # 1-2. FOLLOW-USER

    # /user/user-follow-relation/
    url(r'^user-follow-relation/$', UserFollowRelationCreateView.as_view(),
        name='user-follow-relation'),
    # /user/user-follow-relation/1/
    url(r'^user-follow-relation/(?P<pk>\d+)/$', UserFollowRelationDetailView.as_view(),
        name='user-follow-relation-detail'),
    # /user/1/followers/
    url(r'^(?P<pk>\d+)/followers/$', UserFollowerListView.as_view(),
        name='user-followers'),
    # /user/1/followings/
    url(r'^(?P<pk>\d+)/followings/$', UserFollowingListView.as_view(),
        name='user-followings'),

    # 1-3. FOLLOW-QUESTION

    # /user/question-follow-relation/
    url(r'^question-follow-relation/$', QuestionFollowRelationCreateView.as_view(),
        name='question-follow-relation'),
    # /user/question-follow-relation/1/
    url(r'^question-follow-relation/(?P<pk>\d+)/$', QuestionFollowRelationDetailView.as_view(),
        name='question-follow-relation-detail'),

    # 2. VOTE
    # /user/answer-upvote-relation/
    url(r'^answer-upvote-relation/$', AnswerUpVoteRelationCreateView.as_view(),
        name='answer-upvote-relation'),
    # /user/answer-upvote-relation/1/
    url(r'^answer-upvote-relation/(?P<pk>\d+)/$', AnswerUpVoteRelationDetailView.as_view(),
        name='answer-upvote-relation-detail'),
    # /user/answer-downvote-relation/
    url(r'^answer-downvote-relation/$', AnswerDownVoteRelationCreateView.as_view(),
        name='answer-downvote-relation'),
    # /user/

    # 3. BOOKMARK

    # Profile
    # 1. Profile Main Detail Retrieve/Update
    # /user/1/profile/main-profile/
    url(r'^(?P<pk>\d+)/profile/main-detail/$', ProfileRetrieveUpdateView.as_view(),
        name='profile-main-detail'),

    # 2 Profile Stats
    # /user/1/profile/stats/
    url(r'^(?P<pk>\d+)/profile/stats/$', ProfileStatsRetrieveView.as_view(),
        name='profile-stats'),

    # 3. Profile Employment Credential List/Create
    # /user/1/profile/empl-credentials/
    url(r'^(?P<pk>\d+)/profile/empl-credentials/$', EmploymentCredentialListCreateView.as_view(),
        name='profile-empl-credential-list'),

    # 4. Profile Employment Credential Retrieve, Update, Delete
    # /user/1/profile/empl-credentials/1/
    url(r'^(?P<pk>\d+)/profile/empl-credentials/(?P<credential_pk>\d+)/$', EmploymentCredentialDetailView.as_view(),
        name='profile-empl-credential-detail'),

    # 5. Profile Education Credential List/Create
    # /user/1/profile/edu-credentials/
    url(r'^(?P<pk>\d+)/profile/edu-credentials/$', EducationCredentialListCreateView.as_view(),
        name='profile-edu-credential-list'),

    # 6. Profile Education Credential Retrieve, Update, Delete
    # /user/1/profile/edu-credentials/1/
    url(r'^(?P<pk>\d+)/profile/edu-credentials/(?P<credential_pk>\d+)/$', EducationCredentialDetailView.as_view(),
        name='profile-edu-credential-detail'),

]
