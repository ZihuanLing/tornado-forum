from wtforms_tornado import Form
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Regexp, AnyOf, Length
# from apps.users.models import PasswordField

MOBILE_REGEX = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"


class QuestionForm(Form):
    category = StringField('类别', validators=[DataRequired('请选择类别'), AnyOf(values=['技术问答', '技术分享'])])
    title = StringField('标题', validators=[DataRequired("请输入标题")])
    content = TextAreaField('内容', validators=[DataRequired('请输入内容')])


class AnswerForm(Form):
    content = StringField('内容', validators=[DataRequired('请输入评论内容'),
                                            Length(min=3, message='内容不能少于三个字')])


class AnswerReplyForm(Form):
    replyed_user = IntegerField('回复用户', validators=[DataRequired('请输入回复用户')])
    content = StringField('内容', validators=[DataRequired('请输入评论内容'),
                                            Length(min=3, message='内容不能少于三个字')])



