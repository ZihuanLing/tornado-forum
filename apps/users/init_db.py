from apps.users.models import User
from peewee import MySQLDatabase
from MxForum.settings import settings
database = MySQLDatabase(**settings['db'])


def init():
    database.create_tables([User])


if __name__ == '__main__':
    init()
