from elasticsearch import Elasticsearch
from elasticsearch_dsl.search import Search

my_search = Search(using=Elasticsearch())


def search(query):
    query = my_search.query(
        "multi_match",
        query=query,
        fields=[
            'user',
            'question',
            'text_content',
            '*text_ngram',
        ]
    )
    response = query.execute()
    return response.to_dict()


def all_docs(query):
    return my_search.query('match_all').execute().to_dict()
