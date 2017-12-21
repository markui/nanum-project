import base64
import json
import os

from django.contrib.auth import get_user_model
from rest_framework import status

from config.settings import BASE_DIR
from posts.models import Answer, Question
from posts.tests.custom_base import CustomBaseTest
from topics.models import Topic

User = get_user_model()


class QuillDeltaOperationModelTest(CustomBaseTest):
    def test_qdo_creation(self):
        """
        입력된 content에 대해 빠지는 operation 없이 Quill Delta Operation이 생성되는지 확인
        :return:
        """
        user = User.objects.first()
        question = Question.objects.first()
        content = '{"ops":[{"attributes":{"bold":true},"insert":"bold"},{"insert":"\n"},' \
                  '{"attributes":{"italic":true},"insert":"italic"},{"insert":"\n"},' \
                  '{"attributes":{"italic":true,"bold":true},"insert":"bolditalic"},' \
                  '{"insert":"\n"},{"attributes":{"link":"https://www.youtube.com/watch?v=5rBg_NjFQmc"},' \
                  '"insert":"https://www.youtube.com/watch?v=5rBg_NjFQmc"},{"insert":"\nquote"},' \
                  '{"attributes":{"blockquote":true},"insert":"\n"},{"insert":"print(\'Hello, World!\')"},' \
                  '{"attributes":{"code-block":true},"insert":"\n"},{"insert":"number"},' \
                  '{"attributes":{"list":"ordered"},"insert":"\n"},{"insert":"list"},' \
                  '{"attributes":{"list":"ordered"},"insert":"\n"},{"insert":"bullet"},' \
                  '{"attributes":{"list":"bullet"},"insert":"\n"},{"insert":"list"},' \
                  '{"attributes":{"list":"bullet"},"insert":"\n"},{"insert":"\n"}]}'
        content = json.loads(content, strict=False)
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
        answer = self.create_answer(user=user, question=question, content=content, content_html=html)

        ops_count = len(content['ops'])
        self.assertEqual(answer.quill_delta_operation_set.count(), ops_count)

    def test_image_creation(self):
        """
        content에 들어온 이미지가 포맷에 맞을 경우 400에러가 반환되고 포맷에 맞을경우 201이 반환되는지 확인
        :return:
        """
        user = User.objects.first()
        question = Question.objects.first()

        img_path = os.path.join(
            os.path.join(os.path.join(os.path.join(os.path.join(BASE_DIR, 'posts'), 'tests'), 'test_api'),
                         'answer'), 'image.jpg')
        data = open(img_path, "rb").read()

        # Image File without data:image/jpeg padding
        IMAGE_BASE64 = base64.b64encode(data)
        content = {
            "ops": [
                {
                    "insert": "Test Text\n"
                },
                {
                    "insert": {
                        "image": f"{IMAGE_BASE64}"
                    }
                }
            ]
        }
        content_html = '<div class="ql-editor" data-gramm="false" contenteditable="true" data-placeholder="Compose an epic...">' \
                       '<p>Test Text</p>' \
                       f'<img src="{IMAGE_BASE64}">' \
                       '</div>' \
                       '<div class="ql-clipboard" contenteditable="true" tabindex="-1"></div>' \
                       '<div class="ql-tooltip ql-hidden">' \
                       '<a class="ql-preview" target="_blank" href="about:blank"></a>' \
                       '<input type="text" data-formula="e=mc^2" data-link="https://quilljs.com" data-video="Embed URL">' \
                       '<a class="ql-action"></a>' \
                       '<a class="ql-remove"></a>' \
                       '</div>'
        response = self.create_answer(user=user, question=question, content=content, content_html=content_html,
                                      return_response=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Image File with data:image/jpeg padding
        IMAGE_BASE64 = "data:image/jpeg;base64," + str(IMAGE_BASE64)[2:]
        content = {
            "ops": [
                {
                    "insert": "Test Text\n"
                },
                {
                    "insert": {
                        "image": f"{IMAGE_BASE64}"
                    }
                }
            ]
        }
        content_html = '<div class="ql-editor" data-gramm="false" contenteditable="true" data-placeholder="Compose an epic...">' \
                       '<p>Test Text</p>' \
                       f'<img src="{IMAGE_BASE64}">' \
                       '</div>' \
                       '<div class="ql-clipboard" contenteditable="true" tabindex="-1"></div>' \
                       '<div class="ql-tooltip ql-hidden">' \
                       '<a class="ql-preview" target="_blank" href="about:blank"></a>' \
                       '<input type="text" data-formula="e=mc^2" data-link="https://quilljs.com" data-video="Embed URL">' \
                       '<a class="ql-action"></a>' \
                       '<a class="ql-remove"></a>' \
                       '</div>'
        response = self.create_answer(user=user, question=question, content=content, content_html=content_html,
                                      return_response=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AnswerModelTest(CustomBaseTest):
    def test_answer_string_method(self):
        """
        Answer의 string 함수 테스트
        :return:
        """
        answer = Answer.objects.first()
        answer_user = answer.user
        trimmed_content = answer.text_content[:30]
        answer_str = f'user: {answer_user}, content: {trimmed_content}'
        self.assertEqual(str(answer), answer_str)

    def test_answer_topics_property(self):
        """
        Answer의 topics property 테스트 - 연결된 question의 topics와 일치하는지 확인
        :return:
        """
        answer = Answer.objects.first()
        related_question = answer.question
        self.assertEqual(answer.topics, related_question.topics)

    def test_answer_content_property(self):
        """
        Answer 의 content property 테스트
        :return:
        """
        answer = Answer.objects.first()
        content = answer.content
        self.assertEqual(content, self.ANSWER_DELTA)

    def test_answer_text_content_property(self):
        """
        Answer의 text_content property 테스트
        :return:
        """
        answer = Answer.objects.first()
        text_content = answer.text_content
        self.assertEqual(text_content, 'Test Text')

    def test_answer_related_models_answer_count_increment(self):
        """
        Answer가 생성될 때 연관된 모델들의 answer_count가 increment되는지 확인
        :return:
        """
        user = User.objects.first()
        question = Question.objects.first()
        related_topics = Topic.objects.filter(questions=question)

        question_answer_count_before = question.answer_count
        related_topics_answer_count_before = sum([topic.answer_count for topic in related_topics])

        answer = self.create_answer(user=user, question=question)

        question = Question.objects.first()
        related_topics = Topic.objects.filter(questions=question)

        question_answer_count_after = question.answer_count
        related_topics_answer_count_after = sum([topic.answer_count for topic in related_topics])

        self.assertEqual(question_answer_count_after - question_answer_count_before, 1)
        self.assertEqual(related_topics_answer_count_after - related_topics_answer_count_before, related_topics.count())

    def test_answer_related_modles_answer_count_decrement(self):
        """
        Answer가 삭제될 때 연관된 모델들의 answer_count가 decrement되는지 확인
        """
        answer = Answer.objects.first()
        question = answer.question
        related_topics = answer.topics.all()
        question_answer_count_before = question.answer_count
        related_topics_answer_count_before = sum([topic.answer_count for topic in related_topics])

        answer.delete()

        question = Question.objects.get(pk=question.pk)
        related_topics = Topic.objects.filter(questions=question)
        question_answer_count_after = question.answer_count
        related_topics_answer_count_after = sum([topic.answer_count for topic in related_topics])

        self.assertEqual(question_answer_count_before - question_answer_count_after, 1)
        self.assertEqual(related_topics_answer_count_before - related_topics_answer_count_after, related_topics.count())
