from apps.users.urls import urlpattern as user_urls
from apps.community.urls import urlpattern as community_urls
from tornado.web import StaticFileHandler
from apps.ueditor.urls import urlpattern as ueditor_urls
from apps.questions.urls import urlpattern as question_urls
from apps.message.urls import urlpattern as message_urls
from MxForum.handlers import MainHanler


urlpattern = [
    (r'/?', MainHanler),
    (r'/media/(.*)', StaticFileHandler, {'path': 'media'})
]

urlpattern += user_urls
urlpattern += community_urls
urlpattern += ueditor_urls
urlpattern += question_urls
urlpattern += message_urls
