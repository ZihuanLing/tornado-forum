import requests
import json
import redis
from datetime import datetime
from MxForum.settings import settings
import jwt


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


# web_url = "http://127.0.0.1:8888"
from MxForum.settings import settings

# from peewee import MySQLDatabase
from apps.users.models import User
# db = MySQLDatabase(**settings['db'])

# def test_sms():
#     url = "{}/code/".format(web_url)
#     data = {
#         "mobile": '13725761132',
#     }
#     resp = requests.post(url, json=data)
#     print(resp.text)
#     # print(json.loads(resp.text))


# def test_register():
#     url = "{}/register/".format(web_url)
#     data = {
#         "mobile": '13725761132',
#         'password': '123456789',
#         'code': '5491'
#     }
#     res = requests.post(url, json=data)
#     print(res.content.decode('utf8'))
#     return res

def modify_profile():
    # 修改个人信息
    data = {
        'nick_name': 'LingZihuan',
        'gender': 'male',
        'address': '广东省茂名市',
        'desc': '菜鸡大学生'
    }
    resp = requests.patch(f"{website_url}/info", headers=headers, json=data)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def get_profile():
    resp = requests.get(f"{website_url}/info", headers=headers)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def modify_password():
    # 修改个人信息
    data = {
        'old_password': 'lingzihuan',
        'new_password': '123456789',
        'confirm_password': '123456789',
    }
    resp = requests.post(f"{website_url}/password", headers=headers, json=data)
    print(resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


if __name__ == '__main__':
    # pass
    # redis_conn = redis.StrictRedis(**settings['redis'])
    # r = redis_conn.set("13725761132_5091", 1, 600)
    # print(r)
    # modify_profile()
    # get_profile()
    modify_password()
