from tornado.web import url
from apps.questions.handler import *

urlpattern = [
    ('/questions/?', QuestionHandler),
    ('/questions/([0-9]+)/?', QuestionDetailHandler),
    ('/questions/([0-9]+)/answers/?', AnswerHandler),
    ('/answers/([0-9]+)/replys/?', AnswerReplyHandler),
]
