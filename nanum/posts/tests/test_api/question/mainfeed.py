from django.urls import reverse, resolve

from posts.apis import QuestionMainFeedListView
from .base import QuestionBaseTest


class QuestionMainFeedListViewTest(QuestionBaseTest):
    """
    Question Main-feed에 대하여
    URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    URL이 실제 URL name을 참조하고 있는지 검사
    같은 view의 class인지 검사
    """
    VIEW_CLASS = QuestionMainFeedListView

    # URL name으로 원하는 URL과 실제로 만들어지는 URL 같은지 검사
    def test_question_main_feed_create_url_name_reverse(self):
        print('====reserse(URL NAME)====')
        url = reverse(self.URL_API_QUESTION_MAIN_FEED_LIST_NAME)
        print(url)
        self.assertEqual(url, self.URL_API_QUESTION_MAIN_FEED_LIST)

    # URL이 실제 URL name을 참조하고 있는지 검사
    def test_question_main_feed_create_url_name_resolve(self):
        print('====resolve_match(URL)====')
        resolve_match = resolve(self.URL_API_QUESTION_MAIN_FEED_LIST)
        print(f'{resolve_match.namespace + ":" + resolve_match.url_name}')
        self.assertEqual(resolve_match.namespace + ":" + resolve_match.url_name,
                         self.URL_API_QUESTION_MAIN_FEED_LIST_NAME)

    # 같은 view의 class인지 검사
    # .func 는 임시함수, .as_view() 또한 함수이다. 참조하는 주소 값이 다르므로 .func.view_class 로 비교
    # self.VIEW_CLASS == self.VIEW_CLASS.as_view().view_class : True
    def test_question_main_feed_create_url_resolve_view_class(self):
        """
        posts.apis.question. QuestionMainFeedListView뷰에 대해
        URL reverse, resolve, 사용하고 있는 view함수가 같은지 확인
        :return:
        """
        resolve_match = resolve(self.URL_API_QUESTION_MAIN_FEED_LIST)
        print(f'view class test : {resolve_match.func.view_class}')
        self.assertEqual(resolve_match.func.view_class,
                         self.VIEW_CLASS.as_view().view_class)

    # main-feed
    def test_get_question_main_feed_list(self):
        pass
