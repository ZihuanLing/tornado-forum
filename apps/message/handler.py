import uuid
import os
import json
import aiofiles
from playhouse.shortcuts import model_to_dict
from apps.utils.mxforum_decorators import authenticated_async
from MxForum.handlers import RedisHandler
from MxForum.settings import settings
from apps.utils.util_func import json_serial
from apps.community.forms import *
from apps.community.models import *
from apps.message.models import *


class MessageHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        # 获取当前登录用户的消息
        re_data = []    # 返回的消息
        type_list = self.get_query_arguments('message_type', [])
        if type_list:
            # 这样就取出当前用户的message
            message_query = Message.filter(Message.receiver_id == self.current_user.id,
                                           Message.message_type.in_(type_list))
        else:
            message_query = Message.filter(Message.receiver_id == self.current_user.id)
        messages = await self.application.objects.execute(message_query)
        for message in messages:
            sender = await self.application.objects.get(User, id=message.sender_id)
            re_data.append({
                'sender': {
                    'id': sender.id,
                    'nick_name': sender.nick_name,
                    'head_url': f'/media/{sender.head_url}'
                },
                'message': message.message,
                'message_type': message.message_type,
                'parent_content': message.parent_content,
                'add_time': message.add_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        self.finish(json.dumps(re_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        form = GroupApplyForm.from_json(param)
        if form.validate():
            try:
                group = await self.application.objects.get(CommunityGroup, id=int(group_id))
                existed = await self.application.objects.get(CommunityGroupUser, community=group.id)
                self.set_status(400)
                re_data['non_field'] = '用户已经加入该小组'
            except CommunityGroup.DoesNotExist as e:
                self.set_status(404)
            except CommunityGroupUser.DoesNotExist as e:
                member_info = {
                    'community': group,
                    'user': self.current_user,
                    'apply_reason': form.apply_reason.data
                }
                community_member = await self.application.objects.create(CommunityGroupUser, **member_info)
                re_data['id'] = community_member.id
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]

        self.finish(re_data)