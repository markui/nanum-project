from django.urls import reverse, resolve

from posts.apis import QuestionFilterListView
from .base import QuestionBaseTest


class QuestionFilterListViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionFilterListView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_filter_create_url_name_reverse(self):
        url = reverse(self.URL_API_QUESTION_FILTER_LIST_NAME)
        print(f'reverse test : {url}')
        self.assertEqual(url, self.URL_API_QUESTION_FILTER_LIST)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_filter_create_url_name_resolve(self):
        resolve_match = resolve(self.URL_API_QUESTION_FILTER_LIST)
        print(f'resolve test(url name) : '
              f'{resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name,
                         self.URL_API_QUESTION_FILTER_LIST_NAME)
