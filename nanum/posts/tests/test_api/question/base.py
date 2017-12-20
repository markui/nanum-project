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
    num_of_topics = randrange(1, 10)

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

    # 유저 생성
    @staticmethod
    def create_user(email='siwon@siwon.com', password='dltldnjs', is_none=False):
        if is_none:
            # user단에서 none객체 생성을 막아놓아서 테스트 불가(기본값과 같은 값이 들어가도록 설정)
            # return User.objects.create_user()
            return User.objects.create_user(email=email, password=password)
        return User.objects.create_user(email=email, password=password)

    # 토픽 생성
    @staticmethod
    def create_topic(creator=None, name='temp_topic'):
        return Topic.objects.create(creator=creator, name=name)

    # 질문 생성
    @staticmethod
    def create_question(user=None, content='default : 임시 컨텐츠 입니다.'):
        return Question.objects.create(
            user=user,
            content=content,
        )

    # 랜덤한 다수의 유저 생성 테스트
    def create_random_users(self, is_none=False):
        """
        랜덤한 수의 유저를 생성한다.
        특정 유저를 지정하거나, 랜덤한 유저를 지정할 수 있다.
        params :
            self.num_of_users
        :return: User.objects.all()
        """
        # 랜덤한 수의 유저 생성(is_none : True 일 경우 None객체 생성)
        # user단에서 none객체 생성을 막아놓아서 테스트 불가
        for i in range(self.num_of_users):
            if is_none:
                self.create_user(is_none=True)
            else:
                self.create_user(email=f'user_{i+1}@user.com')
        print(f'User.objects.count() : {User.objects.count()}')
        print(f'num_of_users : {self.num_of_users}')
        self.assertEqual(User.objects.count(), self.num_of_users)
        return User.objects.all()

    # 랜덤한 다수의 토픽 생성 테스트
    def create_random_topics(self, user):
        """
        1. 유저의 pk의 값으로 랜덤한 수의 토픽을 생성한다.
        2. 생성된 토픽들의 pk를 리스트에 저장해 Topic Objects를 리턴한다.
        params :
            self.num_of_users
            self.num_of_topics
        :return: Topic.objects.all()
        """
        # 리턴될 토픽 리스트
        topic_list = list()
        for i in range(self.num_of_topics):
            # 특정 유저(creator)로 다수의 토픽 생성
            if user:
                user = User.objects.get(pk=user.pk)
            # 랜덤한 유저(creator)로 다수의 토픽 생성
            else:
                random_user_pk = randrange(self.num_of_users) + 1
                user = User.objects.get(pk=random_user_pk)

            topic = self.create_topic(creator=user, name=f'토픽 {i+1}')
            # 토픽이 생성될 때 마다 토픽 리스트에 추가
            topic_list.append(topic.pk)

        # print(f'Topic.objects.count() : {Topic.objects.count()}')
        # print(f'num_of_topics : {self.num_of_topics}')
        print(f'====Topic.objects.all()====\n  {Topic.objects.all()}')
        self.assertEqual(Topic.objects.count(), self.num_of_topics)

        # 만들어진 토픽들 리턴(all을 해도 되나 좀 더 명시적으로 작성)
        return Topic.objects.filter(pk__in=topic_list)

    # 랜덤한 다수의 질문 생성 테스트
    def create_random_questions(self):
        """
        1. 질문에 추가 할 토픽들을 만든다.
        2. 만들어진 질문에 토픽의 개수만큼 topic을 추가한다.
        params :
            self.random_user_pk
            self.num_of_topics
        :return: Question.objects.all()
        """
        self.create_random_topics()
        # 질문의 add될 토픽 개수
        num_of_topics_of_question = randrange(self.num_of_topics) + 1

        # 선택된 랜덤한 user로 랜덤한 개수의 questions 생성
        for i in range(self.num_of_questions):
            temp_user = User.objects.get(pk=self.random_user_pk)
            # 질문 생성
            question = self.create_question(
                user=temp_user,
                content=f'{i+1} 컨텐츠 입니다.',
            )
            # 생성된 질문에 토픽 개수만큼 랜덤한 토픽을 추가
            for j in range(num_of_topics_of_question):
                # 랜덤한 토픽 선택
                topic_pk = randrange(self.num_of_topics) + 1
                random_topic = Topic.objects.get(pk=topic_pk)
                # 생성된 질문에 선택된 토픽 추가
                question.topics.add(random_topic)

        self.assertEqual(Question.objects.count(), self.num_of_questions)
        return Question.objects.all()
