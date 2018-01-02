from posts.tests.custom_base import CustomBaseTest


class CommentGetTest(CustomBaseTest):
    """
    url :       /post/comment/<pk>
    method :    GET

    Comment Get에 대한 테스트
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
