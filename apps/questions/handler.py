import uuid
import os
import json
import aiofiles
from playhouse.shortcuts import model_to_dict
from apps.utils.mxforum_decorators import authenticated_async
from MxForum.handlers import RedisHandler
from MxForum.settings import settings
from apps.utils.util_func import json_serial
from apps.questions.forms import *
from apps.questions.models import *
from apps.message.models import Message

class QuestionHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []

        # question_query = Question.select()
        question_query = Question.extend()

        # 根据类别进行划分
        c = self.get_argument('c', None)
        if c:
            question_query.filter(Question.category == c)

        # 排序
        order = self.get_argument('o', None)
        if order:
            if order == 'new':
                question_query = question_query.order_by(Question.add_time.desc())
            elif order == 'hot':
                question_query = question_query.order_by(Question.member_nums.desc())

        # 请求数量
        limit = self.get_argument('limit', None)
        if limit:
            question_query = question_query.limit(int(limit))

        questions = await self.application.objects.execute(question_query)
        for question in questions:
            question_dict = model_to_dict(question)
            question_dict['image'] = f'{settings["SITE_URL"]}/media/{question_dict["image"]}'
            re_data.append(question_dict)

        self.finish(json.dumps(re_data, default=json_serial))
    
    @authenticated_async
    async def post(self, *args, **kwargs):
        re_data = kwargs.get('re_data')
        if not re_data:
            re_data = {}

        status = kwargs.get('status')
        if status == 0:
            self.finish(re_data)
        else:
            # 不能使用json form，因为页面中涉及到图片的选择
            question_form = QuestionForm(self.request.body_arguments)
            if question_form.validate():
                # 需要自己完成图片的验证，wtforms没有提供
                files_meta = self.request.files.get('image', None)
                if not files_meta:
                    self.set_status(400)
                    re_data['image'] = '请上传图片'
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
                    ques_info = {
                        'user': self.current_user,
                        'title': question_form.title.data,
                        'category': question_form.category.data,
                        'content': question_form.content.data,
                        'image': new_filename
                    }
                    question = await self.application.objects.create(Question, **ques_info)
                    re_data['id'] = question.id
            else:
                self.set_status(400)
                for field in question_form.errors:
                    re_data[field] = question_form.errors[field][0]

            self.finish(re_data)


class QuestionDetailHandler(RedisHandler):
    @authenticated_async
    async def get(self, question_id, *args, **kwargs):
        # 获取某个问题的详情
        print('question id: ', question_id)
        re_data = {}
        re_count = 0
        question_details = await self.application.objects.execute(Question.extend().where(Question.id == int(question_id)))
        for data in question_details:
            item_dict = model_to_dict(data)
            re_data = item_dict
            re_data['add_time'] = re_data['add_time'].strftime("%Y-%m-%d")
            re_data['image'] = f'{settings["SITE_URL"]}/media/{re_data["image"]}'
            re_count += 1
        if re_count == 0:
            self.set_status(404)

        self.finish(re_data)


class AnswerHandler(RedisHandler):
    @authenticated_async
    async def get(self, question_id, *args, **kwargs):
        # 获取问题的所有回复
        re_data = []
        try:
            question = await self.application.objects.get(Question, id=int(question_id))
            answers = await self.application.objects.execute(
                Answer.extend().where(Answer.question_id == int(question_id), Answer.parent_answer.is_null(True))
                    .order_by(Answer.add_time.desc())
            )

            for item in answers:
                item_dict = {
                    'id': item.id,
                    'user': model_to_dict(item.user),
                    'content': item.content,
                    'reply_nums': item.reply_nums,
                }

                re_data.append(item_dict)
        except Question.DoesNotExist as e:
            self.set_status(404)
        self.finish(json.dumps(re_data, default=json_serial))

    @authenticated_async
    async def post(self, question_id, *args, **kwargs):
        # 新增评论
        print('question_id: ', question_id)
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        form = AnswerForm.from_json(param)
        if form.validate():
            try:
                question = await self.application.objects.get(Question, id=int(question_id))
                answer = await self.application.objects.create(Answer, user=self.current_user,
                                                               question=question,
                                                               content=form.content.data)
                re_data['id'] = answer.id
                re_data['user'] = {}
                re_data['user']['nick_name'] = self.current_user.nick_name
                re_data['user']['id'] = self.current_user.id

                question.answer_nums += 1   # 更新回答数
                await self.application.objects.update(question)

                # 对问题回答完毕，发送用户消息
                receiver = await self.application.objects.get(User, id=question.user_id)
                await self.application.objects.create(Message, sender=self.current_user, receiver=receiver,
                                                      parent_content=question.content, message=form.content.data,
                                                      message_type=4)

            except Question.DoesNotExist as e:
                self.set_status(404)
                re_data['question'] = '请求的问题不存在'
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]

        self.finish(re_data)



class AnswerReplyHandler(RedisHandler):
    @authenticated_async
    async def get(self, answer_id, *args, **kwargs):
        re_data = []
        try:
            answer = await self.application.objects.execute(Answer.extend().where(Answer.parent_answer_id == int(answer_id)))
            for data in answer:
                item_dict = {
                    'user': {
                        'nick_name': data.user.nick_name
                    },
                    'id': data.id,
                    'content': data.content,
                    'add_time': data.add_time.strftime('%Y-%m-%d'),
                }
                re_data.append(item_dict)

        except Answer.DoesNotExist as e:
            self.set_status(400)
            re_data['post_comm'] = '评论不存在'
        self.finish(json.dumps(re_data, default=json_serial))

    @authenticated_async
    async def post(self, answer_id, *args, **kwargs):
        # 添加回复
        re_data = {}
        param = self.request.body.decode('utf8')
        param = json.loads(param)
        form = AnswerReplyForm.from_json(param)
        if form.validate():
            try:
                answer = await self.application.objects.get(Answer, id=int(answer_id))
                replyed_user = await self.application.objects.get(User, id=form.replyed_user.data)

                reply = await self.application.objects.create(Answer, user=self.current_user,
                                                              parent_answer=answer, reply_user=replyed_user,
                                                              content=form.content.data,
                                                              question_id=1)
                # 回复数量加一
                answer.reply_nums += 1
                await self.application.objects.update(answer)

                re_data['id'] = reply.id
                re_data['user'] = {
                    'id': self.current_user.id,
                    'nick_name': self.current_user.nick_name,
                }

                # 对问题回答完毕，发送用户消息
                await self.application.objects.create(Message, sender=self.current_user, receiver=replyed_user,
                                                      parent_content=answer.content, message=form.content.data,
                                                      message_type=5)

            except Answer.DoesNotExist as e:
                self.set_status(404)
            except User.DoesNotExist as e:
                self.set_status(400)
                re_data['replyed_user'] = '用户不存在'
        else:
            self.set_status(400)
            for field in form.errors:
                re_data[field] = form.errors[field][0]

        self.finish(re_data)
