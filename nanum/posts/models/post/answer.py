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

    @property
    def content(self):
        """
        Answer와 연결된 AnswerContent set을 가지고 와서 quillJS delta 형태로 반환
        :return:
        """
        quill_delta_operation_querydict = self.quill_delta_operation_set.all().order_by('pk')
        if not quill_delta_operation_querydict:
            return ""
        delta_operation_list = list()
        for quill_delta_operation in quill_delta_operation_querydict:
            delta_operation_list.append(quill_delta_operation.delta_operation)
        content = img_processor.create_quill_content(delta_operation_list=delta_operation_list)
        return content

    def save(self, *args, **kwargs):
        super().save()
        post_manager = PostManager.objects.get_or_create(answer=self)


class QuillDeltaOperation(models.Model):
    """
    QuillJS 의 Content중 Operation 한 줄에 대한 정보를 갖는 모델
    해당 content가 쓰인 Answer과 ForeignKey로 연결이 되어 있음
    """
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    attributes = JSONField(null=True, blank=True)
    post = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        related_name='quill_delta_operation_set',
    )

    @property
    def delta_operation(self):
        """
        quill의 operation 하나를 반환
        text 일 경우
        { insert: 'Gandalf', attributes: { bold: true } }

        image 일 경우
        {insert: { image: 'https://octodex.github.com/images/labtocat.png' }}

        :return: quill delta operation
        """
        quill_delta_operation = dict()
        if self.attributes:
            quill_delta_operation['attribute'] = self.attributes
        if self.text:
            quill_delta_operation['insert'] = self.text
        elif self.image:
            image = dict()
            image['image'] = self.image.url
            quill_delta_operation['insert'] = image
        else:
            raise AssertionError(
                "Neither 'text' or 'image' in answer_content. This is an empty instance and should be deleted.")
            return quill_delta_operation
