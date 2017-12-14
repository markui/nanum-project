from elasticsearch_dsl import DocType, Text, Date


class QuestionDocument(DocType):
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    topics = models.ManyToManyField('topics.Topic', related_name='questions')
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    answer_count = models.IntegerField(null=False, default=0)
    bookmark_count = models.IntegerField(null=False, default=0)
    follow_count = models.IntegerField(null=False, default=0)
    comment_count = models.IntegerField(null=False, default=0)
    """
    user = Text(analyzer='korean')
    content = Text(
        multi=True,
        analyzer='korean',
        fields={
            'text_ngram': Text(
                analyzer='edge_ngram_analyzer'
            )
        }
    )
    modified_at = Date()
