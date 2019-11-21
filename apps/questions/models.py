from datetime import datetime

from peewee import *
from MxForum.models import BaseModel
from apps.users.models import User


class Question(BaseModel):
    user = ForeignKeyField(User, verbose_name='用户')
    category = CharField(max_length=200, verbose_name='分类', null=True)
    title = CharField(max_length=200, verbose_name='标题')
    content = TextField(verbose_name='内容')
    image = CharField(max_length=200, verbose_name='图片')
    answer_nums = IntegerField(default=False, verbose_name='回答数')

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)


class Answer(BaseModel):
    # 回答和回复
    user = ForeignKeyField(User, verbose_name='用户', related_name="author")
    question = ForeignKeyField(Question, verbose_name='问题')
    parent_answer = ForeignKeyField('self', verbose_name='回答', null=True, related_name='replied_answer')
    reply_user = ForeignKeyField(User, verbose_name='用户', related_name='replied_author', null=True)
    content = CharField(max_length=1000, verbose_name='内容')
    reply_nums = IntegerField(default=0, verbose_name='回复数')

    @classmethod
    def extend(cls):
        # 1. 多表join
        # 2. 多字段映射同一个model
        author = User.alias()
        reply_user = User.alias()
        return cls.select(cls, Question, author.id, author.nick_name, reply_user.id, reply_user.nick_name)\
            .join(Question, join_type=JOIN.LEFT_OUTER, on=cls.question)\
            .switch(cls).join(author, join_type=JOIN.LEFT_OUTER, on=cls.user)\
            .switch(cls).join(reply_user, join_type=JOIN.LEFT_OUTER, on=cls.reply_user)

