from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from ...models import PostManager
from ...utils.quill_js import QuillJSImageProcessor as img_processor

__all__ = (
    'Answer',
    'QuillDeltaOperation',
)


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    upvote_count = models.IntegerField(null=False, default=0)
    downvote_count = models.IntegerField(null=False, default=0)
    bookmark_count = models.IntegerField(null=False, default=0)

    @property
    def content_first_line(self):
        """
        Answer과 연결된 QuillDeltaOperation set 중 첫번째 줄을 반환
        :return:
        """
        return self.quill_delta_operation_set.order_by('line_no').first()

    @property
    def content(self):
        """
        Answer와 연결된 QuillDeltaOperation set을 가지고 와서 quillJS delta 형태로 반환
        :return:
        """
        quill_delta_operation_querydict = self.quill_delta_operation_set.all().order_by('line_no')
        if not quill_delta_operation_querydict:
            return ""
        delta_operation_list = list()
        for quill_delta_operation in quill_delta_operation_querydict:
            delta_operation_list.append(quill_delta_operation.delta_operation)
        content = img_processor.create_quill_content(delta_operation_list=delta_operation_list)
        return content

    def save(self, *args, **kwargs):
        super().save()
        PostManager.objects.get_or_create(answer=self)


class QuillDeltaOperation(models.Model):
    """
    QuillJS 의 Content중 Operation 한 줄에 대한 정보를 갖는 모델
    해당 content가 쓰인 Post와 ForeignKey로 연결이 되어 있음
    """
    insert_value = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    image_insert_value = JSONField(null=True, blank=True)
    attributes_value = JSONField(null=True, blank=True)
    line_no = models.IntegerField(null=False)
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        related_name='quill_delta_operation_set',
    )

    def __str__(self):
        return f'{self.delta_operation}'

    @property
    def delta_operation(self):
        """
        quill의 operation 하나를 반환
        text 일 경우
        { insert: 'Gandalf', attributes: { bold: true } }

        image 일 경우
        { insert: { image: 'https://octodex.github.com/images/labtocat.png' }}

        :return: quill delta operation
        """
        quill_delta_operation = dict()
        if self.attributes_value:
            quill_delta_operation['attributes'] = self.attributes_value
        if self.insert_value:
            quill_delta_operation['insert'] = self.insert_value
        elif self.image_insert_value:
            quill_delta_operation['insert'] = self.image_insert_value
        else:
            raise AssertionError(
                "Neither 'text' or 'image' in answer_content. This is an empty instance and should be deleted.")
        return quill_delta_operation

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
