from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from posts.models import Answer, Question
from posts.serializers import AnswerGetSerializer, AnswerPostSerializer, AnswerUpdateSerializer
from ...custom_base import CustomBaseTest

User = get_user_model()


class AnswerListTest(CustomBaseTest):
    # Url Reverse 테스트
    def test_answer_list_url_reverse(self):
        url = reverse(self.URL_API_ANSWER_LIST_CREATE_NAME)
        self.assertEqual(url, self.URL_API_ANSWER_LIST_CREATE)

    def test_get_answer_list_when_not_authenticated(self):
        """
        유저가 로그인 되지 않았을 시 401에러를 올리는지 확인
        :return:
        """
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serializer_change_on_request_type(self):
        """
        Request 종류에 따라 serializer가 바뀌는지 확인
        :return:
        """
        get_response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        get_serializer = get_response.renderer_context['view'].get_serializer()

        post_response = self.client.post(self.URL_API_ANSWER_LIST_CREATE)
        post_serializer = post_response.renderer_context['view'].get_serializer()

        self.assertIsInstance(get_serializer, AnswerGetSerializer)
        self.assertIsInstance(post_serializer, AnswerPostSerializer)

    def test_get_list_view_with_wrong_query_params(self):
        """
        URI에 입력 불가능한 query parameter가 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?not_possible=1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_without_query_param_value(self):
        """
        URI에 query parameter가 들어갔는데 값이 안들어 갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?topic=')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_with_query_params_not_matching_type(self):
        """
        Query Parameter에 적합한 type이 아닌 값이 들어갔을 때 에러가 나는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?topic=a')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list_view_single_query_paramter(self):
        """
        가능한 Query parameter에 대해 200 response가 반환되는지 확인 (Page, ordering 제외)
        POSSIBLE QUERY PARAMETERS : topic, user, bookmarked_by

        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        query_paramters = ['topic', 'user', 'bookmarked_by']
        for query in query_paramters:
            response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?{query}=1')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_view_query_topic(self):
        """
        Query Parameter에 Topic으로 필터한 답변의 개수가 실제로 quesiton__topics에 대해 필터한 답변의 개수와 일치하는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?topic=1')
        self.assertEqual(response.data.get('count'), Answer.objects.filter(question__topics=1).count())

    def test_get_list_view_query_user(self):
        """
        Query Parameter에 user으로 필터한 답변의 개수가 실제로 user에 대해 필터한 답변의 개수와 일치하는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?user=1')
        self.assertEqual(response.data.get('count'), Answer.objects.filter(user=1).count())

    def test_get_list_view_query_bookmarked_by(self):
        """
        Query Parameter에 bookmarked_by로 필터한 답변의 개수가
        Answer중 bookmarked user에 user가 포함되는 Answer와 일치하는지 확인
        현재 Bookmark 기능 미개발로 잠정 comment out
        :return:
        """
        # user = User.objects.first()
        # answer = Answer.objects.first()
        # AnswerBookmarkRelation.objects.create(user=user, answer=answer)
        #
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)
        # url= f'{self.URL_API_ANSWER_LIST_CREATE}?bookmarked_by={user.pk}'
        # response = self.client.get(url)
        # self.assertEqual(response.data.get('count'), Answer.objects.filter(answerbookmarkrelation__user=user.pk).count())
        pass

    def test_get_list_with_ordering_query_paramter(self):
        """
        List View가 ordering parameter에 대해 값을 돌려주는지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?ordering=created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?ordering=modified_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_view_with_list_of_values(self):
        """
        Query Parameter에 여러개의 값을 넣어서 필터가 가능한지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(f'{self.URL_API_ANSWER_LIST_CREATE}?user=1,2')
        answers_by_users = Answer.objects.filter(user=1) | Answer.objects.filter(user=2)
        self.assertEqual(response.data.get('count'), answers_by_users.count())

    def test_get_list_pagination_default_pagesize(self):
        """
        List Pagination을 통해 뽑는 page size가 5인지 확인
        :return:
        """
        user = User.objects.first()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.URL_API_ANSWER_LIST_CREATE)
        self.assertEqual(len(response.data['results']), 5)


class AnswerCreateTest(CustomBaseTest):
    def test_create_answer(self):
        """
        Content, Content_html, question과  user가 data에 들어갔을 때 답변이 잘 생성되는지 확인
        :return:
        """
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)
        question = Question.objects.first().pk

        # 답변 생성
        data = {
            'user': u1.pk,
            'question': question,
            'content': self.ANSWER_DELTA,
            'content_html': self.ANSWER_HTML,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        # Status 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 생성된 Answer Object의 content가 집어넣은 Answer Delta와 일치하는지 확인
        answer = Answer.objects.get(pk=response.data['pk'])
        self.assertEqual(answer.content, self.ANSWER_DELTA)

        # 생성된 Answer Object의 content_html이 집어넣은 Answer HTML과 일치하는지 확인
        answer_soup = BeautifulSoup(answer.content_html, 'html.parser')
        original_soup = BeautifulSoup(self.ANSWER_HTML, 'html.parser')
        self.assertEqual(str(answer_soup), str(original_soup))

    def test_create_answer_without_content_unable_to_publish(self):
        """
        Content가 없는 답변에 published가 True인 data가 왔을 때 Error가 반환되는지 확인
        :return:
        """

        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)

        # 답변 생성
        question = Question.objects.first().pk

        data = {
            'user': u1.pk,
            'question': question,
            'published': True,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_answer_without_content_or_content_html(self):
        """
        Content가 왔을 때 content html이 안오거나 content_html이 왔을 때 content가 오면 Error가 반환되는지 확인
        :return:
        """
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)

        # 답변 생성
        question = Question.objects.first().pk

        data = {
            'user': u1.pk,
            'question': question,
            'content': self.ANSWER_DELTA,
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'user': u1.pk,
            'question': question,
            'content_html': self.ANSWER_HTML
        }
        response = self.client.post(self.URL_API_ANSWER_LIST_CREATE, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AnswerUpdateTest(CustomBaseTest):
    def test_non_author_not_able_to_update(self):
        """
        Answer를 작성한 유저 이외의 유저가 업데이트 하려고 할 때 불가능 한지 확인
        :return:
        """
        answer = Answer.objects.first()
        answer_poster = answer.user
        not_answer_poster = User.objects.exclude(pk=answer_poster.pk)[0]
        self.client.force_authenticate(user=not_answer_poster)
        data = {
            'content': self.ANSWER_DELTA,
            'content_html': self.ANSWER_HTML,
        }
        response = self.client.patch(f'/post/answer/{answer.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_serializer_change_on_request_type(self):
        """
        Request 종류에 따라 serializer가 바뀌는지 확인
        :return:
        """
        get_response = self.client.get(f'/post/answer/1/')
        get_serializer = get_response.renderer_context['view'].get_serializer()

        post_response = self.client.patch(f'/post/answer/1/')
        patch_serializer = post_response.renderer_context['view'].get_serializer()

        put_response = self.client.put(f'/post/answer/1/')
        put_serializer = put_response.renderer_context['view'].get_serializer()

        self.assertIsInstance(get_serializer, AnswerGetSerializer)
        self.assertIsInstance(patch_serializer, AnswerUpdateSerializer)
        self.assertIsInstance(put_serializer, AnswerUpdateSerializer)

    def test_update_answer(self):
        """
        제대로된 데이터가 왔을 때 업데이트가 되는지 확인
        :return:
        """
        user = User.objects.first()
        answer = Answer.objects.first()
        self.client.force_authenticate(user=user)
        content = {"ops": [{"attributes": {"bold": True}, "insert": "bold"}, {"insert": "\n"},
                           {"attributes": {"italic": True}, "insert": "italic"}, {"insert": "\n"},
                           {"attributes": {"italic": True, "bold": True}, "insert": "bolditalic"},
                           {"insert": "\n"}, {"attributes": {"link": "https://www.youtube.com/watch?v=5rBg_NjFQmc"},
                                              "insert": "https://www.youtube.com/watch?v=5rBg_NjFQmc"},
                           {"insert": "\nquote"},
                           {"attributes": {"blockquote": True}, "insert": "\n"}, {"insert": "print(\'Hello, World!\')"},
                           {"attributes": {"code-block": True}, "insert": "\n"}, {"insert": "number"},
                           {"attributes": {"list": "ordered"}, "insert": "\n"}, {"insert": "list"},
                           {"attributes": {"list": "ordered"}, "insert": "\n"}, {"insert": "bullet"},
                           {"attributes": {"list": "bullet"}, "insert": "\n"}, {"insert": "list"},
                           {"attributes": {"list": "bullet"}, "insert": "\n"}, {"insert": "\n"}]}
        html = '<div class="ql-editor" data-gramm="false" contenteditable="true" data-placeholder="Compose an epic...">' \
               '<p><strong>bold</strong></p><p><em>italic</em></p><p><strong><em>bolditalic</em></strong></p>' \
               '<p><a href="https://www.youtube.com/watch?v=5rBg_NjFQmc" target="_blank">https://www.youtube.com/watch?v=5rBg_NjFQmc</a></p>' \
               '<blockquote>quote</blockquote><pre class="ql-syntax" spellcheck="false">print("Hello, World!")</pre>' \
               '<ol><li>number</li><li>list</li></ol><ul><li>bullet</li><li>list</li></ul><p><br></p></div>' \
               '<div class="ql-clipboard" contenteditable="true" tabindex="-1"></div>' \
               '<div class="ql-tooltip ql-editing ql-hidden" style="margin-top: -126px; left: 5.375px; top: 82px;" data-mode="link">' \
               '<a class="ql-preview" target="_blank" href="about:blank"></a><' \
               'input type="text" data-formula="e=mc^2" data-link="https://quilljs.com" data-video="Embed URL" placeholder="https://quilljs.com"><a class="ql-action"></a>' \
               '<a class="ql-remove"></a></div>'
        data = {
            'content': content,
            'content_html': html,
        }
        response = self.client.patch(self.URL_API_ANSWER_DETAIL.format(pk=answer.pk), data=data, format='json')
        answer = Answer.objects.get(pk=answer.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(answer.content), content)

    def test_update_answer_without_content_unable_to_publish(self):
        """
        Content가 없는 답변에 published가 True인 data가 왔을 때 Error가 반환되는지 확인
        :return:
        """

        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)
        answer = Answer.objects.first()

        data = {
            'content': None,
            'published': True,
        }
        response = self.client.patch(self.URL_API_ANSWER_DETAIL.format(pk=answer.pk), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_answer_without_content_or_content_html(self):
        """
        Content가 왔을 때 content html이 안오거나 content_html이 왔을 때 content가 오면 Error가 반환되는지 확인
        :return:
        """
        u1_email = self.USER_EMAIL_LIST[0]
        u1 = User.objects.get(email=u1_email)
        self.client.force_authenticate(user=u1)
        answer = Answer.objects.first()

        data = {
            'content': self.ANSWER_DELTA,
        }
        response = self.client.patch(self.URL_API_ANSWER_DETAIL.format(pk=answer.pk), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'content_html': self.ANSWER_HTML
        }
        response = self.client.patch(self.URL_API_ANSWER_DETAIL.format(pk=answer.pk), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
