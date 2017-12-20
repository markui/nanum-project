from random import randrange, randint

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from posts.models import Question
from topics.models import Topic

User = get_user_model()


class QuestionBaseTest(APITestCase):
    # QuestionListCreateView
    URL_API_QUESTION_LIST_CREATE_NAME = 'post:question:list'
    URL_API_QUESTION_LIST_CREATE = '/post/question/'
    # QuestionMainFeedListView
    URL_API_QUESTION_MAIN_FEED_LIST_NAME = 'post:question:main-feed'
    URL_API_QUESTION_MAIN_FEED_LIST = '/post/question/main_feed/'
    # QuestionFilterListView
    URL_API_QUESTION_FILTER_LIST_NAME = 'post:question:topics-filter'
    URL_API_QUESTION_FILTER_LIST = '/post/question/filter/'

    # 생성될 랜덤한 유저의 수
    num_of_users = randint(5, 10)
    # 선택된 랜덤한 유저의 pk
    random_user_pk = randint(1, num_of_users)
    # 선택된 유저가 생성할 질문의 수
    num_of_questions = randint(11, 20)
    # 생성될 랜덤한 토픽의 수
    num_of_topics = randrange(5, 10)

    # query parameters
    query_params = [
        'user',
        'answered_by',
        'bookmarked_by',
        'followed_by',
        'topic',
        'ordering',
        'page',
    ]

    @staticmethod
    def create_user(email='siwon@siwon.com', password='dltldnjs'):
        return User.objects.create_user(email=email, password=password)

    @staticmethod
    def create_topic(creator=None, name='temp_topic'):
        return Topic.objects.create(creator=creator, name=name)

    @staticmethod
    def create_question(user=None, content='default : 임시 컨텐츠 입니다.'):
        return Question.objects.create(
            user=user,
            content=content,
        )

    # 랜덤한 유저 생성
    def create_random_users(self):
        # 랜덤한 개수의 유저 생성
        for i in range(self.num_of_users):
            self.create_user(email=f'user_{i}@user.com')
        print(f'User.objects.count() : {User.objects.count()}')
        print(f'num_of_users : {self.num_of_users}')
        self.assertEqual(User.objects.count(), self.num_of_users)

    # 랜덤한 질문 생성
    def create_random_questions(self):
        self.create_random_topics()
        # 선택된 랜덤한 user로 랜덤한 개수의 questions 생성
        for i in range(self.num_of_questions):
            temp_user = User.objects.get(pk=self.random_user_pk)
            topic_pk = randrange(self.num_of_topics) + 1
            random_topic = Topic.objects.get(pk=topic_pk)

            question = self.create_question(
                user=temp_user,
                content=f'{i} 컨텐츠 입니다.',
            )
            question.topics.add(random_topic)
        self.assertEqual(Question.objects.count(), self.num_of_questions)

    # 랜덤한 토픽 생성
    def create_random_topics(self):
        for i in range(self.num_of_topics):
            random_user_pk = randrange(self.num_of_users) + 1
            random_user = User.objects.get(pk=random_user_pk)

            self.create_topic(creator=random_user, name=f'토픽 : {i}')

        # print(f'Topic.objects.count() : {Topic.objects.count()}')
        # print(f'num_of_topics : {self.num_of_topics}')
        print(f'====Topic.objects.all()====\n  {Topic.objects.all()}')
        self.assertEqual(Topic.objects.count(), self.num_of_topics)
