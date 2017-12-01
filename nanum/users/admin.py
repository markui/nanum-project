from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(
    # user.py
    User,
    # profile.py
    Profile,
    EducationCredentials,
    EmploymentCredentials,
    # relation.py
    # relation - vote
    AnswerUpVoteRelation,
    AnswerDownVoteRelation,
    CommentUpVoteRelation,
    CommentDownVoteRelation,
    # relation - follow
    UserFollowRelation,
    ExpertiseFollowRelation,
    InterestFollowRelation,
    QuestionFollowRelation,
)
