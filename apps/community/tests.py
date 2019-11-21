import json
from datetime import datetime

import requests
import jwt
from MxForum.settings import settings
from peewee import MySQLDatabase
database = MySQLDatabase(**settings['db'])
from apps.community.models import CommunityGroup


website_url = 'http://127.0.0.1:8888'
current_time = datetime.utcnow()

tsessionid_data = jwt.encode({
    'name': 'zihuan',
    'id': 1,
    'exp': current_time,
}, settings['secret_key']).decode('utf8')

headers={
        'tsessionid': tsessionid_data
}


def new_group():
    files = {
        'front_image': open("C:/Users/zihuan.ling/WebstormProjects/MxForum/images/python.png", 'rb'),
    }
    data = {
        'name': '学前教育交流角',
        'desc': '这里是学前教育的交流中心,大家有什么问题可以来一起交流讨论,欢迎提问,学而时习之,不亦乐乎!',
        'notice': '这里是学前教育的交流中心,大家有什么问题可以来一起交流讨论,欢迎提问,学而时习之,不亦乐乎!',
        'category': '教育同盟'
    }
    resp = requests.post('{}/groups/'.format(website_url), headers=headers, data=data, files=files)
    print(resp.status_code)
    print(json.loads(resp.text))


def apply_group(group_id, apply_reason):
    data = {
        'apply_reason': apply_reason,
    }
    resp = requests.post('{}/groups/{}/members/'.format(website_url, group_id), headers=headers, json=data)
    print(resp.status_code)
    print(resp.text)


def get_group(group_id):
    resp = requests.get('{}/groups/{}/'.format(website_url, group_id), headers=headers)
    print("status code: ", resp.status_code)
    print(json.loads(resp.text))


def add_post(group_id):
    # 发帖
    data = {
        'title': 'tornado 入门到实战',
        'content': 'tornado 入门到实战,tornado 入门到实战,tornado 入门到实战'
    }
    resp = requests.post('{}/groups/{}/posts/'.format(website_url, group_id), headers=headers, json=data)
    print("status code: ", resp.status_code)
    print(json.loads(resp.text))


def get_post(post_id):
    resp = requests.get('{}/posts/{}/'.format(website_url, post_id), headers=headers)
    print("status code: ", resp.status_code)
    print(json.loads(resp.text))
    # print(resp.text)


def add_comment(post_id):
    # 发帖
    data = {
        'content': '评论，关于新增消息'
    }
    resp = requests.post('{}/posts/{}/comments'.format(website_url, post_id), headers=headers, json=data)
    print("status code: ", resp.status_code)
    # print(json.loads(resp.text))
    print(resp.text)


def get_comments(post_id):
    resp = requests.get('{}/posts/{}/comments'.format(website_url, post_id), headers=headers)
    print("status code: ", resp.status_code)
    print(json.loads(resp.text))
    # print(resp.text)


def add_reply(comment_id):
    data = {
        'replyed_user': 1,
        'content': '这又是一个评论，惊不惊喜，意不意外！'
    }
    resp = requests.post('{}/comments/{}/replys'.format(website_url, comment_id), headers=headers, json=data)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_reply(comment_id):
    resp = requests.get('{}/comments/{}/replys'.format(website_url, comment_id), headers=headers)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def add_like(comment_id):
    resp = requests.post('{}/comments/{}/likes'.format(website_url, comment_id), headers=headers)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_apply():
    resp = requests.get('{}/applys/'.format(website_url), headers=headers)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


if __name__ == '__main__':
    # new_group()
    # apply_group(1, 'test')
    # get_group(1)
    # add_post(1)
    # get_post(23)
    # add_comment(1)
    # get_comments(1)
    # add_reply(7)
    # get_reply(7)
    # add_like(10)
    # get_apply()
    # query = CommunityGroup.select().filter(CommunityGroup.category=='程序设计')
    query = CommunityGroup.extend().filter(CommunityGroup.category=='程序设计')
    print(query)
    res = database.execute(query)
    print(res.fetchall())
