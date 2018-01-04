from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.reverse import reverse

from posts.utils.filters import CommentFilter
from posts.utils.pagination import CommentPagination
from users.models import CommentUpVoteRelation, CommentDownVoteRelation
from ..models import Comment, CommentPostIntermediate, Answer, Question

__all__ = (
    'CommentCreateSerializer',
    'CommentSerializer',
)


class PostHyperLinkRelatedField(serializers.HyperlinkedRelatedField):
    def get_url(self, obj, view_name, request, format):
        model = obj.__class__.__name__.lower()
        view_name = view_name.format(model=model)
        url_kwargs = {
            'pk': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class BaseCommentserializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        view_name='user:profile-main-detail',
        read_only=True,
    )
    related_post = PostHyperLinkRelatedField(
        lookup_field='related_post_pk',
        view_name='post:{model}:{model}-detail',
        read_only=True,
    )
    parent = serializers.HyperlinkedRelatedField(
        view_name='post:comment:comment-detail',
        read_only=True,
    )
    user_upvote_relation = serializers.SerializerMethodField()
    user_downvote_relation = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name='post:comment:comment-detail',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            'pk',
            'url',
            'user',
            'related_post',
            'parent',
            'content',
            'created_at',
            'modified_at',
            'user_upvote_relation',
            'user_downvote_relation',
            'upvote_count',
            'downvote_count',
        ]
        read_only_fields = [
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'user_upvote_relation',
            'user_downvote_relation',
            'upvote_count',
            'downvote_count',
        ]

    @property
    def request(self):
        return self.context.get("request")

    @property
    def request_user(self):
        """
        Check if AnonymousUser
        :return:
        """
        return self.request.user

    def get_user_upvote_relation(self, obj):
        if self.request_user.is_authenticated():
            try:
                relation_pk = CommentUpVoteRelation.objects.get(user=self.request_user, comment=obj).pk
                view_name = 'user:comment-upvote-relation-detail'
                kwargs = {'pk': relation_pk}
                return reverse(view_name, kwargs=kwargs, request=self.request)
            except CommentUpVoteRelation.DoesNotExist:
                return

    def get_user_downvote_relation(self, obj):
        if self.request_user.is_authenticated():
            try:
                relation_pk = CommentDownVoteRelation.objects.get(user=self.request_user, comment=obj).pk
                view_name = 'user:comment-downvote-relation-detail'
                kwargs = {'pk': relation_pk}
                return reverse(view_name, kwargs=kwargs, request=self.request)
            except CommentDownVoteRelation.DoesNotExist:
                return


class CommentGetSerializer(BaseCommentserializer):
    pass


class CommentCreateSerializer(BaseCommentserializer):
    """
    METHOD: CREATE
    """
    question = serializers.IntegerField(required=False, write_only=True)
    answer = serializers.IntegerField(required=False, write_only=True)

    class Meta(BaseCommentserializer.Meta):
        """
        fields = __all__ + question + answer
        read_only_fields = __all__ - parent
        """
        fields = BaseCommentserializer.Meta.fields.copy()
        fields.append('question')
        fields.append('answer')

        read_only_fields = BaseCommentserializer.Meta.read_only_fields.copy()
        read_only_fields.remove('parent')

    def validate_answer(self, value):
        try:
            Answer.objects.get(pk=value)
        except:
            raise ParseError({"error": "해당 pk의 답변이 존재하지 않습니다."})
        return value

    def validate_question(self, value):
        try:
            Question.objects.get(pk=value)
        except:
            raise ParseError({"error": "해당 pk의 질문이 존재하지 않습니다."})
        return value

    def validate(self, data):
        """
        Answer 혹은 Question값이 필수적으로 들어왔는지 Validate
        - Refactor 가능한지?
        :param data:
        :return:
        """
        if not data.get('answer', None) and not data.get('question', None):
            raise ParseError({"error": "Question, Answer 중 한개의 값은 있어야 합니다."})
        return data

    def save(self, **kwargs):
        """
        serializers.py 의 save method override
        validated_data에서 question 과 answer를 통해 comment 연결된 CommentPostIntermediate object를 get,
        해당 값을 넣어 Comment를 저장

        :param kwargs:
        :return:
        """
        question = self.validated_data.pop("question", None)
        answer = self.validated_data.pop("answer", None)
        if question:
            comment_post_intermediate = CommentPostIntermediate.objects.get(question=question)
        elif answer:
            comment_post_intermediate = CommentPostIntermediate.objects.get(answer=answer)
        else:
            raise ParseError(detail={"error": "Question, Answer 중 한개의 값은 있어야 합니다."})

        super().save(
            user=self.request_user,
            comment_post_intermediate=comment_post_intermediate,
            **kwargs
        )


class CommentSerializer(BaseCommentserializer):
    """
    METHOD: GET, PUT, PATCH
    """
    paginator = CommentPagination()
    filter_backend = filters.DjangoFilterBackend
    filter_class = CommentFilter

    immediate_children = serializers.SerializerMethodField()
    all_children = serializers.SerializerMethodField()

    class Meta(BaseCommentserializer.Meta):
        """
        fields = __all__ + immediate_children + all_children
        read_only_fields = __all__ + immediate_children + all_children
        """
        model = Comment
        fields = BaseCommentserializer.Meta.fields.copy()
        fields.extend(
            ['immediate_children', 'all_children', 'immediate_children_count', 'all_children_count'])

        read_only_fields = BaseCommentserializer.Meta.read_only_fields.copy()
        read_only_fields.extend(
            ['immediate_children', 'all_children', 'immediate_children_count', 'all_children_count'])

    @property
    def view(self):
        return self.context['view']

    # Filter -> Pagniate  -> Serializer -> return
    # REST API list() 참조
    def get_immediate_children(self, obj):
        qs = obj.immediate_children
        queryset = self.filter_backend().filter_queryset(request=self.request, queryset=qs, view=self.view)
        page = self.paginator.paginate_queryset(request=self.request, queryset=queryset)
        children_serializer = CommentGetSerializer(page, many=True, context={'request': self.request})
        paginated_response = self.paginator.get_paginated_response(children_serializer.data)
        return paginated_response.data

    def get_all_children(self, obj):
        qs = obj.all_children
        queryset = self.filter_backend().filter_queryset(request=self.request, queryset=qs, view=self.view)
        page = self.paginator.paginate_queryset(request=self.request, queryset=queryset)
        children_serializer = CommentGetSerializer(page, many=True, context={'request': self.request})
        paginated_response = self.paginator.get_paginated_response(children_serializer.data)
        return paginated_response.data

    def __init__(self, *args, **kwargs):
        """
        Override serializer __init__
        Serializer가 initialize가 되기전에 동적으로 immediate_children 을 표기할 지 all_children을 표기할지를 결정

        :param args:
        :param kwargs:
        """
        query_params = kwargs.get('context').get('request').query_params
        non_query_params = {"immediate_children", "all_children"} - query_params.keys()
        if non_query_params:
            for param in non_query_params:
                self.fields.pop(param)
        super().__init__(*args, **kwargs)
