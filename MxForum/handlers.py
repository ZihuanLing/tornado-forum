from abc import ABC

from tornado.web import RequestHandler

import redis

from MxForum.settings import settings
from apps.utils.mxforum_decorators import authenticated_async


class BaseHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE, PUT, PATCH')
        self.set_header('Access-Control-Max-Age', '*')
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, tsessionid, Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Max-Age')

    def get(self, *args, **kwargs):
        print('get uri : ', self.request.uri)

    def post(self, *args, **kwargs):
        print('post uri: ', self.request.uri)

    def options(self, *args, **kwargs):
        pass


class RedisHandler(BaseHandler, ABC):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis(**settings['redis'])


class MainHanler(BaseHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        # 此处请求的是/index.html，如果验证通过的话重定向到group
        # 如果用户没有登录的话在验证的时候就将用户定向到登录页面
        re_data = {
            'verify_status': 'OK',
            'redirect': '/html/group/group.html'
        }
        self.finish(re_data)

    async def post(self, *args, **kwargs):
        self.set_status(404)
