import json
from datetime import datetime

import requests
import jwt
from MxForum.settings import settings

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


def new_question():
    files = {
        'image': open("C:/Users/neill/Pictures/Saved Pictures/solong.jpeg", 'rb'),
    }
    data = {
        'title': 'This is title',
        'content': '这里是学前教育的交流中心,大家有什么问题可以来一起交流讨论,欢迎提问,学而时习之,不亦乐乎!',
        'category': '技术问答'
    }
    resp = requests.post('{}/questions/'.format(website_url), headers=headers, data=data, files=files)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_question():
    resp = requests.get('{}/questions/'.format(website_url), headers=headers)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_question_detail(question_id):
    resp = requests.get('{}/questions/{}'.format(website_url, question_id), headers=headers)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)



def add_answer(question_id):
    data = {
        'content': '今天天气真好！！',
    }
    resp = requests.post('{}/questions/{}/answers/'.format(website_url, question_id), headers=headers, json=data)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_answer(question_id):
    resp = requests.get('{}/questions/{}/answers/'.format(website_url, question_id), headers=headers)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def add_reply(answer_id):
    data = {
        'replyed_user': 1,
        'content': '这是一个关于回答的评论，惊不惊喜，意不意外！'
    }
    resp = requests.post('{}/answers/{}/replys'.format(website_url, answer_id), headers=headers, json=data)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_reply(answer_id):
    resp = requests.get('{}/answers/{}/replys'.format(website_url, answer_id), headers=headers)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


if __name__ == '__main__':
    # new_question()
    # get_question()
    # get_question_detail(1)
    add_answer(1)
    # get_answer(1)
    add_reply(1)
    # get_reply(1)
