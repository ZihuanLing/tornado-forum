from peewee import *
from MxForum.models import BaseModel
from bcrypt import hashpw, gensalt


class PasswordHash(bytes):
    def check_password(self, password):
        password = password.encode('utf-8')
        return hashpw(password, self) == self


class PasswordField(BlobField):
    def __init__(self, iterations=12, *args, **kwargs):
        if None in (hashpw, gensalt):
            raise ValueError('Missing library required for PasswordField: bcrypt')
        self.bcrypt_iterations = iterations
        self.raw_password = None
        super(PasswordField, self).__init__(*args, **kwargs)

    def db_value(self, value):
        """Convert the python value for storage in the database."""
        if isinstance(value, PasswordHash):
            return bytes(value)

        if isinstance(value, str):
            value = value.encode('utf-8')
        salt = gensalt(self.bcrypt_iterations)
        return value if value is None else hashpw(value, salt)

    def python_value(self, value):
        """Convert the database value to a pythonic value."""
        if isinstance(value, str):
            value = value.encode('utf-8')

        return PasswordHash(value)

GENDERS = (
    ('female', '女'),
    ('male', '男')
)


class User(BaseModel):
    mobile = CharField(max_length=11, verbose_name='手机号码', index=True, unique=True)
    # 密码的加密和比对？
    # 1. 密文
    # 2. 不可反解
    password = PasswordField(verbose_name='密码')
    nick_name = CharField(max_length=20, verbose_name='昵称', null=True)
    head_url = CharField(max_length=200, verbose_name='头像', null=True)
    address = CharField(max_length=200, verbose_name='地址', null=True)
    desc = TextField(verbose_name='个人简介', null=True)
    gender = CharField(max_length=22, verbose_name='性别', null=True, choices=GENDERS)
