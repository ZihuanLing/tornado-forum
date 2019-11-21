from MxForum.settings import settings
from apps.community.models import *
from apps.questions.models import *
from apps.message.models import Message


database = MySQLDatabase(**settings['db'])


def init():
    database.create_tables([User])
    database.create_tables([CommunityGroup, CommunityGroupUser])
    database.create_tables([PostComment, Post, CommentLike])
    database.create_tables([Question, Answer])
    database.create_tables([Message])


if __name__ == '__main__':
    init()
