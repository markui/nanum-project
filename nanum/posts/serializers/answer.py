from itertools import chain

from django.db.models import QuerySet
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from users.models import AnswerUpVoteRelation, AnswerBookmarkRelation
from ..models import Answer, QuillDeltaOperation
from ..utils.quill_js import DjangoQuill

__all__ = (
    'AnswerPostSerializer',
    'AnswerUpdateSerializer',
    'AnswerGetSerializer',
)

django_quill = DjangoQuill(model=QuillDeltaOperation, parent_model=Answer)


class AnswerPostSerializer(serializers.ModelSerializer):
    content = serializers.JSONField(default=None)

    class Meta:
        model = Answer
        fields = (
            'pk',
            'user',
            'question',
            'content',
            'content_html',
            'published',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'created_at',
            'modified_at'
        )

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

    def validate(self, data):
        """
        published가 True인데 content가 비어있을 경우 validation error 를 raise
        :param data:
        :return:
        """
        if not data['content'] and data['published']:
            raise ParseError({"error": "Content 가 없는 답변은 Publish가 불가능합니다."})
        if data.get('content') and not data.get('content_html'):
            raise ParseError({"error": "Content 가 왔으나 Content_html 이 없습니다."})
        if data.get('content_html') and not data.get('content'):
            raise ParseError({"error": "Content_html 이 왔으나 Content 가 없습니다."})

        return data

    def save(self, **kwargs):
        """
        Answer 객체를 만들고 content를 AnswerContent로 변환하여 저장
        :param kwargs:
        :return:
        """
        content = self.validated_data.pop('content', None)
        content_html = self.validated_data.pop('content_html', None)
        # request_user를 **kwargs에 추가하여 super().save() 호출
        with atomic():
            answer_instance = super().save(user=self.request_user, **kwargs)
            if not content or not content_html:
                return answer_instance
            self._save_quill_delta_operation(
                content=content,
                answer_instance=answer_instance
            )
            self._save_content_html(
                content_html=content_html
            )

    def _save_quill_delta_operation(self, content, answer_instance):
        """

        :param content:
        :param answer_instance:
        :return:
        """
        instances = django_quill.get_delta_operation_instances(
            content=content,
            parent_instance=answer_instance
        )
        if not instances:
            raise ParseError({"error": "content가 잘못된 포맷입니다. "})
        QuillDeltaOperation.objects.bulk_create(instances)

    def _save_content_html(self, content_html):
        """

        :param content_html:
        :return:
        """
        img_delta_objs = self.instance.quill_delta_operation_set.exclude(image='').order_by('line_no')
        html = django_quill.img_base64_to_link(
            objs=img_delta_objs,
            html=content_html
        )
        self.instance.content_html = html
        self.instance.save(update_fields=['content_html'])


class AnswerUpdateSerializer(AnswerPostSerializer):
    content = serializers.JSONField(default=None)

    class Meta:
        model = Answer
        fields = (
            'pk',
            'user',
            'question',
            'content',
            'content_html',
            'published',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'created_at',
            'modified_at'
        )

    def save(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        queryset = self.instance.quill_delta_operation_set.all()
        content = self.validated_data.pop('content', None)
        content_html = self.validated_data.pop('content_html', None)
        if not content or not content_html:
            return
        with atomic():
            self._update_quill_delta_operation(queryset=queryset, content=content)
            self._save_content_html(content_html=content_html)

    def _update_quill_delta_operation(self, queryset: QuerySet, content: str):
        """

        :param queryset: self.instance와 연결되어있는 QuillDeltaOperation Queryset
        :param content: Update할 Content
        :return:
        """
        to_update_list, to_create_list, to_delete_list = django_quill.update_delta_operation_list(
            queryset=queryset,
            content=content,
            parent_instance=self.instance,
        )
        for inst in chain(to_update_list, to_create_list):
            inst.save()
        for inst in to_delete_list:
            inst.delete()


class AnswerGetSerializer(serializers.ModelSerializer):
    user_upvote_relation = serializers.SerializerMethodField()
    user_bookmark_relation = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            'pk',
            'user',
            'question',
            'content_html',
            'upvote_count',
            'comment_count',
            'user_upvote_relation',
            'user_bookmark_relation',
            'published',
            'created_at',
            'modified_at',
        )
        read_only_fields = (
            'pk',
            'user',
            'question',
            'content_html',
            'upvote_count',
            'comment_count',
            'user_upvote_relation',
            'user_bookmark_relation',
            'published',
            'created_at',
            'modified_at',
        )

    @property
    def request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    # Relation ManyToMany로 엮인 값들에 대해서 pk를 반환
    def get_user_upvote_relation(self, obj):
        try:
            return AnswerUpVoteRelation.objects.get(user=self.request_user, answer=obj).pk
        except:
            return None

    def get_user_bookmark_relation(self, obj):
        try:
            return AnswerBookmarkRelation.objects.get(user=self.request_user, answer=obj).pk
        except:
            return None
