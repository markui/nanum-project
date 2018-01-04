from django.contrib.auth import get_user_model
from rest_framework import status

from posts.models import Answer
from posts.serializers import AnswerGetSerializer, AnswerUpdateSerializer
from ...custom_base import CustomBaseTest

User = get_user_model()


class AnswerUpdateTest(CustomBaseTest):
    """
    url :       /post/answer/
    method :    PUT, PATCH

    Answer UPDATE에 대한 테스트

    """

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
