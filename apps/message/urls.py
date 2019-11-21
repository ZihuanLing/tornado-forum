from tornado.web import url
from apps.message.handler import *

urlpattern = [
    ('/messages/?', MessageHandler),
]
