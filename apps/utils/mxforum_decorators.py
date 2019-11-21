import functools
import jwt
from tornado.web import RequestHandler

from MxForum.settings import settings
from apps.users.models import User


def authenticated_async(method):

    @functools.wraps(method)
    async def wrapper(self: RequestHandler, *args, **kwargs):
        kwargs['status'] = 0
        tsessionid = self.request.headers.get('tsessionid')
        re_data = {}
        authenticated_OK = False    # 验证是否通过
        if not tsessionid:
            self.redirect('/login.html')
        elif tsessionid == 'null' or tsessionid == 'undefined':
            self.set_status(401)
            re_data['tsessionid'] = '请传入合法的tsessionid！'
            self.finish(re_data)
        else:
            try:
                # 解码通过headers传过来的tsessionid数据
                data = jwt.decode(tsessionid, settings['secret_key'], leeway=settings['jwt_expire'])
                # 解码正常
                user_id = data['id']
                # print('tsession data: ', data)
                try:
                    # 从数据库中获取到user并设置给_current_user
                    cur_user = await self.application.objects.get(User, id=user_id)
                    self._current_user = cur_user
                    # print("Nick name: ", cur_user.nick_name)
                    # print("current user: ", self.current_user)
                    kwargs['status'] = 1
                    authenticated_OK = True
                except User.DoesNotExist as e:
                    self.set_status(401)
                    re_data['user'] = '用户不存在'
            except jwt.exceptions.InvalidSignatureError as e:
                self.set_status(401)
                re_data['tsessionid'] = "签名不一致"
            except jwt.exceptions.DecodeError as e:
                self.set_status(401)
                re_data['tsessionid'] = '非法签名！'
                print(e)
                print('用户传入了非法签名：', tsessionid)
            except jwt.exceptions.ExpiredSignatureError as e:
                # token 过期了，重定向到登录页面
                self.set_status(400)
                re_data['tsessionid'] = '会话已过期'
                self.redirect("/login.html")
            kwargs['re_data'] = re_data
            if authenticated_OK:
                await method(self, *args, **kwargs)

    return wrapper
