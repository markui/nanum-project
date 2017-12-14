from elasticsearch_dsl import DocType, Text


class TopicDocType(DocType):
    """

    """
    name = Text(
        analyzer='korean',
        fields={
            'text_ngram': Text(
                analyzer='edge_ngram_analyzer'
            )
        }
    )