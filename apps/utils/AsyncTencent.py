# coding: utf-8
# 用协程发送短信
import hashlib
import time
import json
from random import randint
from json import dumps

from tornado import httpclient
from tornado.httpclient import HTTPRequest


class AsyncTencent:
    # 腾讯短信验证码发送
    # POST https://yun.tim.qq.com/v5/tlssmssvr/sendsms?sdkappid=xxxxx&random=xxxx
    url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms?'

    def __init__(self, sdkappid, appkey):
        self.url = self.url + "sdkappid="+sdkappid
        self.appkey = appkey
        self.params = {
            "ext": "",
            "extend": "",
            "params": [],
            "sig": "",
            "sign": "TRYSKY",
            "tel": {
                "mobile": "",
                "nationcode": "86"
            },
            "time": 0,
            "tpl_id": 458489
        }

    def cal_signature(self, random, _time, mobile):
        # 用sha256算法加密计算短信签名
        string = f'appkey={self.appkey}&random={random}&time={_time}&mobile={mobile}'
        sig = hashlib.sha256(string.encode())
        return sig.hexdigest()

    async def send_single_sms(self, mobile: str, content: list):
        http_client = httpclient.AsyncHTTPClient()
        rand = randint(10000, 100000)   # 生成一个随机数
        self.url += "&random="+str(rand)
        print(self.url)
        _time = int(time.time())
        sig = self.cal_signature(rand, _time, mobile)

        self.params['sig'] = sig
        self.params['time'] = _time
        self.params['tel']['mobile'] = mobile
        self.params['params'] = content

        body = bytes(dumps(self.params).encode())
        post_request = HTTPRequest(url=self.url, method='POST', body=body, headers={'Content-Type': 'application/json'})
        resp = await http_client.fetch(post_request)
        return json.loads(resp.body.decode('utf8'))
        # print(resp)


if __name__ == '__main__':
    sdkappid = 'your sdk appid'
    appkey = 'you appkey'
    tc = AsyncTencent(sdkappid, appkey)

    from tornado import ioloop
    io_loop = ioloop.IOLoop()

    from functools import partial
    # 使用partial来传递参数
    send_single_sms = partial(tc.send_single_sms, '10086', ['123456', 5])

    io_loop.run_sync(send_single_sms)
