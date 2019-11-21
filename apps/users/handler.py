import uuid
import os
import json
from abc import ABC
from random import choice
from datetime import datetime

import aiofiles
import jwt
from apps.users.forms import *
from apps.utils.AsyncTencent import AsyncTencent
from MxForum.handlers import RedisHandler
from MxForum.settings import settings
from apps.users.models import User
from apps.utils.mxforum_decorators import authenticated_async


def generate_code():
    # 生成随机4位验证码
    seeds = '123457890'
    rand_str = []
    for _ in range(4):
        rand_str.append(choice(seeds))
    return ''.join(rand_str)


class LoginHandler(RedisHandler):
    async def post(self, *args, **kwargs):
        re_data = {}

        param = self.request.body.decode('utf8')
        param = json.loads(param)
        # print("param: ", param)
        login_form = LoginForm.from_json(param)

        if login_form.validate():
            # 验证通过，从数据库判断
            mobile = login_form.mobile.data
            password = login_form.password.data

            try:
                user = await self.application.objects.get(User, mobile=mobile)
                # 用户存在，检查密码是否对应
                if not user.password.check_password(password):
                    self.set_status(400)
                    re_data["non_fields"] = '用户名或密码错误'
                else:
                    # 登录成功
                    # 1. 是否rest api只能使用jwt？ -- 不是，session
                    # 前后端分离的系统可以布置在两个不同的域名之下
                    # session 是服务器随机生成的字符串，保存在服务器中 -- 相对于jwt来说是更加安全的
                    # jwt 本质上还是加密技术 - 使用密码将文本加密
                    # 此处生成json web token
                    payload = {
                        "id": user.id,
                        "user": user.nick_name,
                        "exp": datetime.utcnow()
                    }
                    token = jwt.encode(payload, settings['secret_key'], algorithm='HS256')
                    re_data['id'] = user.id
                    if user.nick_name is not None:
                        re_data['nick_name'] = user.nick_name
                    else:
                        re_data['nick_name'] = user.mobile

                    re_data['token'] = token.decode('utf8')
            except User.DoesNotExist as e:
                # 当前用户不存在
                self.set_status(400)
                re_data['mobile'] = '用户不存在'

        self.finish(re_data)


class RegisterHandler(RedisHandler, ABC):
    async def post(self, *args, **kwargs):
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        register_form = RegisterForm.from_json(param)
        if register_form.validate():
            mobile = register_form.mobile.data
            code = register_form.code.data
            password = register_form.password.data
            # 数据库验证 - 验证码是否正确
            redis_key = f"{mobile}_{code}"
            # print(redis_key)
            # redis 是一个同步io - 查询是内存，非常快
            if not self.redis_conn.get(redis_key):
                self.set_status(400)
                re_data['code'] = 'The code is invalidate or expired'
            else:
                # 验证用户是否存在
                try:
                    existed_user = await self.application.objects.get(User, mobile=mobile)
                    # 用户是存在的
                    re_data['info'] = 'This phone number has been registered!'
                except User.DoesNotExist as e:
                    # 到此说明用户不存在，创建新用户
                    user = await self.application.objects.create(User, mobile=mobile, password=password)
                    re_data['id'] = user.id
        else:
            self.set_status(400)
            for field in register_form.errors:
                re_data[field] = register_form.errors[field][0]

        self.finish(re_data)


class SmsHandler(RedisHandler, ABC):

    async def post(self, *args, **kwargs):
        # 前端发送过来的是一个json数据
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)

        # 猴子补丁？
        sms_form = SmsCodeForm.from_json(param)
        if sms_form.validate():
            mobile = sms_form.mobile.data

            code = generate_code()  # 生成一个验证码
            ex = 10  # 过期时间十分钟

            tc = AsyncTencent(**settings['TencentSMS'])

            re_json = await tc.send_single_sms(mobile, [code, ex])
            # print(re_json)
            if re_json['result'] != 0:
                self.set_status(400)
                re_data['mobile'] = re_json['errmsg']
            else:
                # 将验证码写入到redis中并设置过期时间
                self.redis_conn.set('{}_{}'.format(mobile, code), 1, ex * 60)
        else:
            self.set_status(400)
            for field in sms_form.errors:
                re_data[field] = sms_form.errors[field][0]

        self.finish(re_data)


class ProfileHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            'mobile': self.current_user.mobile,
            'nick_name': self.current_user.nick_name,
            'address': self.current_user.address,
            'gender': self.current_user.gender,
            'desc': self.current_user.desc,
        }
        self.finish(re_data)

    @authenticated_async
    async def patch(self, *args, **kwargs):
        # patch方法 - 局部更新
        # 不是使用post或者put方法 - 这种是新建
        # 我们修改个人信息的时候是更新部分字段
        # patch字段是专门用来更新部分字段的
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        profile_form = ProfileForm.from_json(param)
        if profile_form.validate():
            self.current_user.nick_name = profile_form.nick_name.data
            self.current_user.gender = profile_form.gender.data
            self.current_user.address = profile_form.address.data
            self.current_user.desc = profile_form.desc.data

            await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in profile_form.errors:
                re_data[field] = profile_form.errors[field]

        self.finish(re_data)


class HeadImageHandler(RedisHandler):
    # 修改头像的Handler
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = kwargs.get('re_data')
        re_data['image'] = ''
        if self.current_user.head_url:
            re_data['image'] = "/media/" + self.current_user.head_url
        self.finish(re_data)

    @authenticated_async
    async def post(self, *args, **kwargs):
        re_data = kwargs.get('re_data')
        # 取图片
        file_metas = self.request.files.get('image', None)
        if not file_metas:
            self.set_status(400)
            re_data['image'] = '请上传图片'
        else:
            # 保存图片，不能使用传统的图片（文件）读写方式
            # 传统的是同步的，会阻塞
            # 这里使用aiofiles
            for meta in file_metas:
                filename = meta['filename']
                new_filename = f"{uuid.uuid1()}_{filename}"
                file_path = os.path.join(self.settings['MEDIA_ROOT'], new_filename)
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(meta['body'])
            self.current_user.head_url = new_filename
            await self.application.objects.update(self.current_user)
            re_data['image'] = "/media/" + new_filename
        self.finish(re_data)


class PasswordHandler(RedisHandler):
    @authenticated_async
    async def post(self, *args, **kwargs):
        # 修改密码
        re_data = kwargs.get('re_data')
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        password_form = ChangePasswordForm.from_json(param)
        if password_form.validate():
            # 检查旧密码
            if not self.current_user.password.check_password(password_form.old_password.data):
                self.set_status(400)
                re_data['old_password'] = '旧密码错误'
            else:
                if password_form.new_password.data != password_form.confirm_password.data:
                    self.set_status(400)
                    re_data['new_password'] = '两次密码不一致'
                else:
                    self.current_user.password = password_form.new_password.data
                    await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in password_form.errors:
                re_data[field] = password_form.errors[field]
        self.finish(re_data)
