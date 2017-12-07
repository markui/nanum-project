import base64
import os

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APITestCase

from config.settings import BASE_DIR
from posts.models import Question, Answer
from topics.models import Topic

User = get_user_model()


class AnswerBaseTest(APITestCase):
    URL_API_ANSWER_LIST_CREATE_NAME = 'post:answer:list_create'
    URL_API_ANSWER_MAIN_FEED_LIST_NAME = 'post:answer:list_main_feed'
    URL_API_ANSWER_LIST_CREATE = '/post/answer/'
    URL_API_ANSWER_MAIN_FEED_LIST = '/post/answer/main_feed/'
    URL_FILTER_USER = 'user={pk}'
    URL_FILTER_TOPIC = 'topic={pk}'
    URL_FILTER_BOOKMARKED = 'bookmarked={pk}'
    URL_FILTER_ORDERING = 'ordering={field}'

    USER_EMAIL_LIST = [
        'abc1@abc.com',
        'abc2@abc.com',
        'abc3@abc.com',
        'abc4@abc.com'
    ]
    TOPIC_NAME_LIST = [
        '컴공',
        '음악',
        '술',
        '우주과학'
    ]
    QUESTION_CONTENT = '{topic} - {user}의 질문'

    img_path = os.path.join(os.path.join(os.path.join(os.path.join(BASE_DIR, 'posts'), 'tests'), 'test_api'),
                                   'image.jpg')
    with open(img_path, 'rb') as image:
        data = image.read()
    data = base64.b64encode(data)
    print(data)
    data_decode = base64.b64decode(data)
    print(data_decode)
    IMAGE_BASE64 = base64.b64decode(data_decode)
    print(IMAGE_BASE64)


    content = "{question} - {user}의 답변"
    ANSWER_CONTENT = {
        "ops": [
            {
                "insert": content
            },
            {
                "insert": {
                    "image": f"{IMAGE_BASE64}"
                }
            }
        ]
    }

    @classmethod
    def create_user(cls, name, email):
        return User.objects.create_user(name=name, email=email, password='password')

    @classmethod
    def create_topic(cls, user=None, name=None):
        return Topic.objects.create(creator=user, name=name)

    @classmethod
    def create_question(cls, user=None, topic=None):
        content = cls.QUESTION_CONTENT.format(topic=topic, user=user)
        q = Question.objects.create(user=user, content=content)
        q.topics.add(topic)
        return q

    @classmethod
    def create_answer(cls, user=None, question=None):
        content = cls.content.format(question=question, user=user)
        client = Client()
        cls.ANSWER_CONTENT['ops'][0]["insert"] = content
        data = {
            'user': user,
            'question': question,
            'content': cls.ANSWER_CONTENT,
        }
        return client.post(cls.URL_API_ANSWER_LIST_CREATE, data=data)

    @classmethod
    def setUpTestData(cls):

        # 유저 생성
        users = []
        for email in cls.USER_EMAIL_LIST:
            user = cls.create_user(name=email, email=email)
            users.append(user)

        # Topic 생성
        # 유저 1 - Topic 1, 유저 2 - Topic 2,... 유저 n - Topic n
        topics = []
        for i, topic_name in enumerate(cls.TOPIC_NAME_LIST):
            topic = cls.create_topic(user=users[i],
                                     name=topic_name)
            topics.append(topic)

        # Question 생성
        # T = Question with Topic
        # 유저 1 - T 1, T 2, T 3, T 4, 유저 2 - T 1, T 2, T 3, T 4,...
        # 총 len(user) * len(topic) 만큼의 질문 생성
        questions = []
        for user in users:
            for topic in topics:
                question = cls.create_question(user=user, topic=topic.pk)
                questions.append(question)

        # Answer 생성
        # T{pk}_U{pk} = Q with T pk, U pk
        # 유저 1 - T1_U1, T1_U2, T1_U3, T1_U4, T2_U1...유저 2 - T1_U1,...
        # 총 len(user) * len(question) 만큼의 답변 생성
        answers = []
        for user in users:
            for topic in topics:
                for question_user in users:
                    question = Question.objects.get(user=question_user, topics=topic)
                    answer = cls.create_answer(user=user, question=question)
                    answers.append(answer)

