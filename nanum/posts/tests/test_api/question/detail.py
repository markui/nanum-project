from rest_framework import status

from posts.apis import QuestionRetrieveUpdateDestroyView
from .base import QuestionBaseTest


class QuestionRetrieveUpdateDestroyViewTest(QuestionBaseTest):
    VIEW_CLASS = QuestionRetrieveUpdateDestroyView

    def test_question_create_and_retrieve_object(self):
        temp_user = self.create_user()
        temp_question = self.create_question(user=temp_user)
        print(f'temp_question : {temp_question.pk}')

        response = self.client.get(f'http://testserver/post/question/{temp_question.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)