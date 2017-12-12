from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.reverse import reverse

from posts.utils.filters import CommentFilter
from posts.utils.pagination import CommentPagination
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


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    METHOD: CREATE
    user, parent, question, answer, content를 데이터로 받음
    CommentPostIntermediate을 통해 question / answer과 연결되며, related_post로 해당 정보를 보여줌
    """
    question = serializers.IntegerField(required=False, write_only=True)
    answer = serializers.IntegerField(required=False, write_only=True)
    user = serializers.HyperlinkedRelatedField(
        view_name='user:profile-detail',
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

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'content',
            'question',
            'answer',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'related_post',
            'created_at',
            'modified_at',
        )

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
            raise ParseError(detail="Question, Answer 중 한개의 값은 있어야 합니다.")
        return data

    @property
    def request_user(self):
        """
        Request를 보낸 유저를 반환
        :return:
        """
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

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


class CommentGetSerializer(serializers.ModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        view_name='user:profile-detail',
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

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'upvote_count',
            'downvote_count',
            'all_children_count',
        )
        read_only_fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'upvote_count',
            'downvote_count',
            'all_children_count',
            'content',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CommentSerializer(CommentGetSerializer):
    """
    METHOD: GET
    모든 값이 read_only
    all_children_count, 즉 밑에 달린 댓글의 총 개수 또한 반환
    """
    paginator = CommentPagination()
    filter_backend = filters.DjangoFilterBackend
    filter_class = CommentFilter

    immediate_children = serializers.SerializerMethodField()
    all_children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'upvote_count',
            'downvote_count',
            'all_children_count',
            'immediate_children',
            'all_children',
        )
        read_only_fields = (
            'pk',
            'user',
            'related_post',
            'parent',
            'created_at',
            'modified_at',
            'upvote_count',
            'downvote_count',
            'all_children_count',
            'content',
        )

    @property
    def request(self):
        return self.context.get('request')

    @property
    def view(self):
        return self.context['view']

    # Filter -> Pagniate  -> Serializer -> return
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
