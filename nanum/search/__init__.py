from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

# connections.create_connection(hosts=['nanum-elasticsearch.be'], timeout=20)
# connections.create_connection(host='nanum-elasticsearch.be', port=9200)
# [{'host': 'nanum-elasticsearch.be/', 'port': 80, 'use_ssl': True}]
# es = Elasticsearch([{'host': 'nanum-elasticsearch.be', 'port': 9200, "timeout":30, "retry_on_timeout":True}])
# print(es.info())