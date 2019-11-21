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


def get_messages():
    # resp = requests.get('{}/messages/?'.format(website_url), headers=headers)
    resp = requests.get('{}/messages/?message_type=1&message_type=2'.format(website_url), headers=headers)
    print("status code: ", resp.status_code)
    try:
        print(json.loads(resp.text))
    except json.decoder.JSONDecodeError as e:
        print(resp.text)


def add_comment(post_id):
    # 发帖
    data = {
        'content': 'tornado 入门到实战,tornado 入门到实战,tornado 入门到实战'
    }
    resp = requests.post('{}/posts/{}/comments'.format(website_url, post_id), headers=headers, json=data)
    print("status code: ", resp.status_code)
    # print(json.loads(resp.text))
    print(resp.text)


if __name__ == '__main__':
    get_messages()
