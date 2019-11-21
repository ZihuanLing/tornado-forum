# 所谓的装饰器到底是怎么样的？
# add 方法
import time
from datetime import datetime
import functools
import jwt


def time_dec(func):
    print("dec started.")
    # 当从外部引用装饰器的时候，会直接运行装饰器内部的代码
    # 因此，需要用一个wrapper来对里面的代码进行封装
    # 可以将返回的wrapper理解为一个指针

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 这个方法接受的参数是一个函数
        st = time.time()
        func(*args, **kwargs)
        et = time.time()
        print("last time: ", et - st)
    print('dec end, returning')
    return wrapper      # 闭包的思想


# python 装饰器的加载过程

@time_dec
def add(a, b):
    # 如果我要打印这个函数的执行时间？
    print('add start.')
    # time.sleep(3)
    print(a, b, a + b)
    return a + b


if __name__ == '__main__':
    # 变量如何传递到wrapper
    # print(add.__name__)
    # res = add(1, 2)
    # print(res)
    key = 'hello#abc'
    # payload = {
    #     "id": 1,
    #     "user": 'zihuan',
    #     "exp": datetime.utcnow()
    # }
    # token = jwt.encode(payload, key=key, algorithm='HS256').decode('utf8')
    # print(token)
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlciI6InppaHVhbiIsImV4cCI6MTU3NDEyOTU2NX0.NmVtOPHrQiJL0UkObXLWMzR81iLeeZED3f7ziwtJez0'
    content = jwt.decode(token, key=key, leeway=10)
    print(content)
