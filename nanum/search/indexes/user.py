from elasticsearch_dsl import DocType, Text


class UserDocType(DocType):
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
