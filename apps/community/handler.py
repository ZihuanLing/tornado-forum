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
from apps.message.models import Message


class GroupDetailHandler(RedisHandler):
    @authenticated_async
    async def get(self, group_id, *args, **kwargs):
        re_data = {}
        try:
            group = await self.application.objects.get(CommunityGroup, id=int(group_id))
            # 获取数据
            item_dict = {}
            item_dict['id'] = group.id
            item_dict['name'] = group.name
            item_dict['category'] = group.category
            item_dict['desc'] = group.desc
            item_dict['notice'] = group.notice
            item_dict['member_nums'] = group.member_nums
            item_dict['front_image'] = f'{settings["SITE_URL"]}/media/{group.front_image}'
            re_data = item_dict
        except CommunityGroup.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)


class GroupMemberHandler(RedisHandler):
    @authenticated_async
    async def post(self, group_id, *args, **kwargs):
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


class GroupHandler(RedisHandler):
    async def get(self, *args, **kwargs):
        re_data = []

        # community_query = CommunityGroup.select()
        community_query = CommunityGroup.extend()

        # 根据类别进行划分
        c = self.get_query_argument('c', None)
        if c and c != 'new':
            community_query = community_query.filter(CommunityGroup.category==c)

        # 排序
        order = self.get_query_argument('o', None)
        if order:
            if order == 'new':
                community_query = community_query.order_by(CommunityGroup.add_time.desc())
            elif order == 'hot':
                community_query = community_query.order_by(CommunityGroup.member_nums.desc())

        # 请求数量
        limit = self.get_query_argument('limit', None)
        if limit:
            community_query = community_query.limit(int(limit))

        groups = await self.application.objects.execute(community_query)
        for group in groups:
            group_dict = model_to_dict(group)
            group_dict['front_image'] = f'{settings["SITE_URL"]}/media/{group_dict["front_image"]}'
            re_data.append(group_dict)

        self.finish(json.dumps(re_data, default=json_serial))

    @authenticated_async
    async def post(self, *args, **kwargs):
        # 创建一个新的小组
        re_data = kwargs.get('re_data')
        if not re_data:
            re_data = {}
        print("re_data: ", re_data)

        status = kwargs.get('status')
        if status == 0:
            self.finish(re_data)
        else:
            # 不能使用json form，因为页面中涉及到图片的选择
            group_form = CommunityGroupForm(self.request.body_arguments)
            if group_form.validate():
                # 需要自己完成图片的验证，wtforms没有提供
                files_meta = self.request.files.get('front_image', None)
                if not files_meta:
                    self.set_status(400)
                    re_data['front_image'] = '请上传图片'
                else:
                    # 保存图片，不能使用传统的图片（文件）读写方式
                    # 传统的是同步的，会阻塞
                    # 这里使用aiofiles
                    for meta in files_meta:
                        filename = meta['filename']
                        new_filename = f"{uuid.uuid1()}_{filename}"
                        file_path = os.path.join(self.settings['MEDIA_ROOT'], new_filename)
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(meta['body'])
                    group_info = {
                        'add_user': self.current_user,
                        'name': group_form.name.data,
                        'category': group_form.category.data,
                        'desc': group_form.desc.data,
                        'notice': group_form.notice.data,
                        'front_image': new_filename,
                        'member_nums': 1,   # 默认是1，将创建者加入小组
                    }
                    group = await self.application.objects.create(CommunityGroup, **group_info)
                    re_data['id'] = group.id
                    # 小组创建完毕之后，将创建者加入当前的小组
                    member_info = {
                        'user': self.current_user,
                        'community': group,
                        'status': 'agree',
                    }
                    new_member = await self.application.objects.create(CommunityGroupUser, **member_info)
                    re_data['new_member'] = new_member.id
            else:
                self.set_status(400)
                for field in group_form.errors:
                    re_data[field] = group_form.errors[field][0]

            self.finish(re_data)


class PostHandler(RedisHandler):
    @authenticated_async
    async def get(self, group_id, *args, **kwargs):
        post_list = []
        # 获取小组内的帖子
        try:
            group = await self.application.objects.get(CommunityGroup, id=int(group_id))
            group_member = await self.application.objects.get(CommunityGroupUser, user=self.current_user,
                                                              community=int(group_id), status="agree")

            post_query = Post.extend()
            # 根据类别进行划分
            c = self.get_argument('cate', None)
            if c == 'hot':
                post_query = post_query.filter(Post.is_hot == True)
            if c == 'excellent':
                post_query = post_query.filter(Post.is_excellent == True)

            posts = await self.application.objects.execute(post_query)

            for post in posts:
                item_dict = {
                    'user': {
                        'id': post.user.id,
                        'nick_name': post.user.nick_name,
                        'head_url': f"/media/{post.user.head_url}"
                    },
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'comment_nums': post.comment_nums
                }
                post_list.append(item_dict)
        except CommunityGroupUser.DoesNotExist as e:
            self.set_status(403)
        except CommunityGroup.DoesNotExist as e:
            self.set_status(404)

        self.finish(json.dumps(post_list, default=json_serial))

    @authenticated_async
    async def post(self, group_id, *args, **kwargs):
        # 发布新的帖子
        re_data = {}

        try:
            group = await self.application.objects.get(CommunityGroup, id=int(group_id))
            group_member = await self.application.objects.get(CommunityGroupUser, user=self.current_user,
                                                              community=int(group_id), status="agree")

            param = self.request.body.decode('utf8')
            param = json.loads(param)
            form = PostForm.from_json(param)
            if form.validate():
                post_info = {
                    'user': self.current_user,
                    'title': form.title.data,
                    'content': form.content.data,
                    'group': group
                }
                post = await self.application.objects.create(Post, **post_info)
                re_data['id'] = post.id
            else:
                self.set_status(400)
                for field in form.errors:
                    re_data[field] = form.errors[field]
        except CommunityGroup.DoesNotExist as e:
            self.set_status(404)
        except CommunityGroupUser.DoesNotExist as e:
            self.set_status(403)
            re_data['user'] = '组内用户不存在，你应该先申请加入该小组'
            # 403 表示权限不存在

        self.finish(re_data)


class PostDetailHandler(RedisHandler):
    @authenticated_async
    async def get(self, post_id, *args, **kwargs):
        # 获取某个帖子的详情
        print('postid: ', post_id)
        re_data = {}
        re_count = 0
        post_details = await self.application.objects.execute(Post.extend().where(Post.id == int(post_id)))
        for data in post_details:
            item_dict = {
                'user': model_to_dict(data.user),
                'title': data.title,
                'content': data.content,
                'comment_nums': data.comment_nums,
                'add_time': data.add_time.strftime("%Y-%m-%d")
            }
            item_dict['user']['head_url'] = f'/media/{item_dict["user"]["head_url"]}'
            re_data = item_dict
            re_count += 1
        if re_count == 0:
            self.set_status(404)

        self.finish(re_data)


class PostCommentHandler(RedisHandler):
    @authenticated_async
    async def get(self, post_id, *args, **kwargs):
        # 获取帖子的所有评论
        re_data = []
        try:
            post = await self.application.objects.get(Post, id=int(post_id))
            post_comments = await self.application.objects.execute(
                PostComment.extend().where(PostComment.post_id == int(post_id),
                                           PostComment.parent_comment.is_null(True))
                    .order_by(PostComment.add_time.desc())
            )

            for item in post_comments:
                has_liked = False
                try:
                    comments_like = await self.application.objects.get(CommentLike, post_comment_id=item.id,
                                                                       user=self.current_user)
                    has_liked = True
                except CommentLike.DoesNotExist as e:
                    pass

                item_dict = {
                    'id': item.id,
                    'user': {
                        'nick_name': item.user.nick_name,
                        'id': item.user.id,
                        'head_url': f'/media/{item.user.head_url}'
                    },
                    'content': item.content,
                    'reply_nums': item.reply_nums,
                    'like_nums': item.like_nums,
                    'has_nums': has_liked,
                }

                re_data.append(item_dict)
        except Post.DoesNotExist as e:
            self.set_status(404)
        self.finish(json.dumps(re_data, default=json_serial))

    @authenticated_async
    async def post(self, post_id, *args, **kwargs):
        # 新增评论
        print('post_id: ', post_id)
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        form = PostCommentForm.from_json(param)
        if form.validate():
            try:
                post = await self.application.objects.get(Post, id=int(post_id))
                post_comment = await self.application.objects.create(PostComment, user=self.current_user,
                                                                     post=post, content=form.content.data)
                re_data['id'] = post_comment.id
                re_data['user'] = {}
                re_data['user']['nick_name'] = self.current_user.nick_name
                re_data['user']['id'] = self.current_user.id

                # 评论新增完毕，创建一个用户的消息
                receiver = await self.application.objects.get(User, id=post.user_id)
                await self.application.objects.create(Message, sender=self.current_user, receiver=receiver,
                                                      parent_content=post.title, message=form.content.data,
                                                      message_type=1)

            except Post.DoesNotExist as e:
                self.set_status(404)
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]

        self.finish(re_data)


class CommentReplyHandler(RedisHandler):
    @authenticated_async
    async def get(self, comment_id, *args, **kwargs):
        re_data = []
        try:
            comments = await self.application.objects.execute(
                PostComment.extend().where(PostComment.parent_comment == int(comment_id)))
            for data in comments:
                item_dict = {
                    'user': {
                        'nick_name': data.user.nick_name,
                        'head_url': f"/media/{data.user.head_url}"
                    },
                    'id': data.id,
                    'content': data.content,
                    'add_time': data.add_time.strftime('%Y-%m-%d'),
                    'comment_num': data.reply_nums,
                    'like_nums': data.like_nums
                }
                re_data.append(item_dict)

        except PostComment.DoesNotExist as e:
            self.set_status(400)
            re_data['post_comm'] = '评论不存在'
        self.finish(json.dumps(re_data, default=json_serial))

    @authenticated_async
    async def post(self, comment_id, *args, **kwargs):
        # 添加回复
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        form = CommentReplyForm.from_json(param)
        if form.validate():
            try:
                comment = await self.application.objects.get(PostComment, id=int(comment_id))
                replyed_user = await self.application.objects.get(User, id=form.replyed_user.data)

                reply = await self.application.objects.create(PostComment, user=self.current_user,
                                                              parent_comment=comment, replyed_user=replyed_user,
                                                              content=form.content.data)
                # 回复数量加一
                comment.reply_nums += 1
                await self.application.objects.update(comment)

                # 回复完毕，创建一个用户的消息
                await self.application.objects.create(Message, sender=self.current_user, receiver=replyed_user,
                                                      parent_content=comment.content, message=form.content.data,
                                                      message_type=2)

                re_data['id'] = reply.id
                re_data['user'] = {
                    'id': self.current_user.id,
                    'nick_name': self.current_user.nick_name,
                }

            except PostComment.DoesNotExist as e:
                self.set_status(404)
            except User.DoesNotExist as e:
                self.set_status(400)
                re_data['replyed_user'] = '用户不存在'
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]

        self.finish(re_data)


class CommentLikeHandler(RedisHandler):
    @authenticated_async
    async def post(self, comment_id, *args, **kwargs):
        re_data = {}
        try:
            comment = await self.application.objects.get(PostComment, id=int(comment_id))
            has_liked = await self.application.objects.get(CommentLike, user_id=self.current_user.id,
                                                           post_comment_id=int(comment_id))
            self.set_status(400)
            re_data['like'] = '请勿重复点赞'
        except PostComment.DoesNotExist as e:
            self.set_status(404)
            re_data['comment'] = '评论不存在'
        except CommentLike.DoesNotExist as e:
            # 没有重复点赞
            comment_like = await self.application.objects.create(CommentLike, user=self.current_user,
                                                                 post_comment=comment)
            comment.like_nums += 1
            re_data['id'] = comment_like.id
            await self.application.objects.update(comment)

            # 点赞完毕，创建一个用户的消息
            receiver = await self.application.objects.get(User, id=comment.user_id)
            await self.application.objects.create(Message, sender=self.current_user, receiver=receiver,
                                                  parent_content=comment.content, message="",
                                                  message_type=3)

        self.finish(re_data)


class ApplyHandler(RedisHandler):
    # 处理加入小组申请
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []
        all_groups = await self.application.objects.execute(
            CommunityGroup.select().where(CommunityGroup.add_user_id == self.current_user.id))
        all_group_ids = [group.id for group in all_groups]
        # print("all group ids: ", all_group_ids)
        group_member_query = CommunityGroupUser.extend().where(CommunityGroupUser.community_id.in_(all_group_ids),
                                                               CommunityGroupUser.status.is_null(True))
        all_members = await self.application.objects.execute(group_member_query)
        for member in all_members:
            re_data.append({
                'user': {
                    'id': member.user.id,
                    'nick_name': member.user.nick_name,
                    'head_url': f'/media/{member.user.head_url}'
                },
                'group': member.community.name,
                'id': member.id,
                'apply_reason': member.apply_reason,
                'add_time': member.add_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        self.finish(json.dumps(re_data))


class HandleApplyHandler(RedisHandler):
    @authenticated_async
    async def patch(self, apply_id, *args, **kwargs):
        # 处理某一条数据的通过或不通过
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        form = HandleApplyForm.from_json(param)
        if form.validate():
            status = form.status.data
            handle_msg = form.handle_msg.data
            try:
                member = await self.application.objects.get(CommunityGroupUser, id=int(apply_id))
                group_id = member.community_id
                group = await self.application.objects.get(CommunityGroup, id=group_id)

                member.status = status
                member.handle_msg = handle_msg
                member.handle_time - datetime.now()

                # 处理完毕，如果审核通过，小组成员加一
                print('form status: ', form.status.data)
                print('apply reason: ', form.handle_msg.data)
                if form.status.data == 'agree':
                    group.member_nums += 1
                    await self.application.objects.update(group)
                await self.application.objects.update(member)
            except CommunityGroupUser.DoesNotExist as e:
                self.set_status(404)
            except CommunityGroup.DoesNotExist as e:
                self.set_status(403)
                re_data['community group'] = '该小组已不存在'
        else:
            for field in form.errors:
                re_data[field] = form.errors[field]

        self.finish(re_data)
