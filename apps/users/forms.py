from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp, AnyOf
# from apps.users.models import PasswordField

MOBILE_REGEX = "^[1][3-9][0-9]{9}$"


class SmsCodeForm(Form):
    mobile = StringField("手机号码", validators=[
        DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号")
    ])


class LoginForm(Form):
    mobile = StringField("手机号码", validators=[
        DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号")
    ])
    # 密码的长度为8 - 18
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])


class RegisterForm(Form):
    mobile = StringField("手机号码", validators=[
        DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号")
    ])
    # 验证码长度为4
    code = StringField("验证码", validators=[DataRequired(message="请输入验证码")])
    # 密码的长度为8 - 18
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])


class ProfileForm(Form):
    nick_name = StringField('昵称', validators=[DataRequired('请输入昵称')])
    gender = StringField('性别', validators=[AnyOf(values=['female', 'male'])])
    address = StringField('地址', validators=[DataRequired('请输入地址')])
    desc = StringField('个人简介')


class ChangePasswordForm(Form):
    old_password = StringField('旧密码', validators=[DataRequired('请输入旧密码')])
    new_password = StringField('新密码', validators=[DataRequired('请输入新密码')])
    confirm_password = StringField('新密码', validators=[DataRequired('请输入新密码')])
