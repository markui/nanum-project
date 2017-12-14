import elasticsearch
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from elasticsearch5 import Elasticsearch
from elasticsearch5.helpers import bulk
from elasticsearch_dsl import DocType, Text, Date, Index

from posts.models import Answer
from search.analyzers import korean, ngram, edge_ngram_analyzer

__all__ = (
    'AnswerDocument',
    'AnswerIndex',
    'create',
    'delete'
)


class AnswerDocument(DocType):
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    content_html = models.TextField(null=False, blank=True)
    upvote_count = models.IntegerField(null=False, default=0)
    downvote_count = models.IntegerField(null=False, default=0)
    bookmark_count = models.IntegerField(null=False, default=0)
    comment_count = models.IntegerField(null=False, default=0)
    text_content
    """
    user = Text(analyzer='korean')
    question = Text(
        multi=True,
        analyzer='korean',
        fields={
            'question_ngram': Text(
                analyzer='edge_ngram_analyzer'
            )
        }
    )
    text_content = Text(
        multi=True,
        analyzer='korean',
        fields={
            'text_content_ngram': Text(
                analyzer='edge_ngram_analyzer'
            )
        }
    )
    created_at = Date()
    modified_at = Date()

    class Meta:
        index = "answer"
        doc_type = "answer"


class AnswerIndex(Index):
    doctype = AnswerDocument
    index_name = "answer"

    def create(self, **kwargs):
        """
        blogpost Index를 생성
        :return:
        """
        self.analyzer(korean)
        self.analyzer(ngram)
        self.analyzer(edge_ngram_analyzer)
        self.doc_type(AnswerIndex.doctype)
        super().create(**kwargs)

    @staticmethod
    def bulk_indexing():
        """
        Answer 의 모든 객체들을 Elasticsearch 서버에 generator로 전달하여 Indexing을 실시
        성공한 개수와 실패했을 경우 실패에 대해 출력
        :return:
        """
        result = bulk(client=Elasticsearch(),
                      actions=(create(sender=Answer, instance=answer) for
                               answer
                               in
                               Answer.objects.iterator()))
        return f'success : {result[0]}  failed : {result[1]}'


@receiver(post_save, sender=Answer, )
def create(sender: Answer, instance: Answer, created: bool = True, **kwargs):
    """
    Answer 객체가 save되는 시점에 document를 생성
    이미 생성된 객체에 대해서는 update_document를 호출
    :param sender: Blogpost 객체
    :param instance: Blogpost 객체 - Answer의 생성된 Instance
    :param created: Boolean 값 - 생성된 Instance가 새로 생성되었으면 True, 이미 있었다면 False
    :return:
    """
    index = Index("answer")
    try:
        if not index.exists():
            AnswerIndex("answer").create()
        obj = AnswerDocument(
            meta={'id': instance.id},
            user=instance.user.name,
            question=instance.question.content,
            text_content=instance.text_content,
            created_at=instance.created_at,
            modified_at=instance.modified_at,
        )
        obj.save()
        return obj.to_dict(include_meta=True)
    except elasticsearch.exceptions.ConnectionError:
        return


@receiver(post_delete, sender=Answer, )
def delete(sender: Answer, instance: Answer, **kwargs):
    """
    Answer 객체가 delete되는 시점에 document를 삭제

    :return:

    """
    try:
        doc = AnswerDocument.get(id=instance.pk)
        doc.delete()
    except:
        pass
