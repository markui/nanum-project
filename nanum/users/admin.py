from django.contrib import admin

from .models import *

# Register your models here.
user_models = [
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
]

admin.site.register(user_models)
