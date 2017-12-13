from elasticsearch_dsl import analyzer, tokenizer

# Tokenizers
ngram_tokenizer = tokenizer(
    'ngram_tokenizer',
    'nGram',
    min_gram=1,
    max_gram=5,
    token_chars=["letter", "digit", "punctuation", "symbol"]
)

edge_ngram_tokenizer = tokenizer(
    'edge_ngram_tokenizer',
    'edgeNGram',
    min_gram=1,
    max_gram=5,
    token_chars=["letter", "digit", "punctuation", "symbol"]
)

korean = analyzer(
    'korean',
    type='custom',
    tokenizer="mecab_ko_standard_tokenizer",
)

ngram = analyzer(
    'ngram_analyzer',
    type='custom',
    tokenizer=ngram_tokenizer,
    filter=["lowercase", "trim"]
)

edge_ngram_analyzer = analyzer(
    'edge_ngram_analyzer',
    type='custom',
    tokenizer=edge_ngram_tokenizer,
    filter=["lowercase", "trim"]
)

edge_ngram_analyzer_reverse = analyzer(
    'edge_ngram_analyzer_reverse',
    type='custom',
    tokenizer=edge_ngram_tokenizer,
    filter=["lowercase", "trim", "reverse"]
)  # edge_ngram_analyzer_back = analyzer(
#     'edge_ngram_analyzer_back',
#     type='custom',
#     tokenizer='edge_ngram_tokenizer',
#     filter=["lowercase", "trim", "edge_ngram_filter_back"]
# )
