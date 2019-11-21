from tornado.web import url
from apps.users.handler import *

urlpattern = [
    # code - 实际上是一个RESTful规范，不要包含动词
    url("/code/?", SmsHandler),
    url("/register/?", RegisterHandler),
    url("/login/?", LoginHandler),
    url("/info/?", ProfileHandler),
    # 修改头像通常使用独立接口使用
    # 比如在后端进行裁剪之类的操作，以适应web端的显示
    url("/headimages/?", HeadImageHandler),
    url("/password/?", PasswordHandler),
]