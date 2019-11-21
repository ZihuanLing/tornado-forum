import hashlib
import time
from random import randint

import requests


class Tencent:
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

    def send_single_sms(self, mobile: str, content: list):
        rand = randint(10000, 100000)   # 生成一个随机数
        self.url += "&random="+str(rand)
        print(self.url)
        _time = int(time.time())
        sig = self.cal_signature(rand, _time, mobile)
        self.params['sig'] = sig
        self.params['time'] = _time
        self.params['tel']['mobile'] = mobile
        self.params['params'] = content
        # print(self.params)
        resp = requests.post(self.url, json=self.params)
        print(resp)


if __name__ == '__main__':
    sdkappid = 'your sdk appid'
    appkey = 'you appkey'
    tc = Tencent(sdkappid, appkey)
    tc.send_single_sms('10086', ['123456', 5])
