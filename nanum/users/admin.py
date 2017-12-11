from django.contrib import admin

from .models import *

# Register your models here.
user_models = [
    # user.py
    User,
    # profile.py
    Profile,
    EducationCredential,
    EmploymentCredential,
    # relation.py
    # relation - vote
    AnswerUpVoteRelation,
    AnswerDownVoteRelation,
    CommentUpVoteRelation,
    CommentDownVoteRelation,
    # relation - follow
    # UserFollowRelation,
    # ExpertiseFollowRelation,
    # InterestFollowRelation,
    # QuestionFollowRelation,
]

admin.site.register(user_models)


@admin.register(ExpertiseFollowRelation)
class ExpertiseFollowRelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic']


@admin.register(InterestFollowRelation)
class InterestFollowRelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic']


@admin.register(QuestionFollowRelation)
class QuestionFollowRelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']


@admin.register(UserFollowRelation)
class UserFollowRelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'target']