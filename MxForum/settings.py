import os

import peewee_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = {
    # 指定静态文件的路径 - 指定static_path有利于在html文件中使用static_url()访问
    'static_path': 'C:/Users/zihuan.ling/PycharmProjects/mxTornado/MxForum/static',
    'static_url_prefix': '/static/',                # 静态文件的访问前缀 - localhost:8888/static
    'template_path': 'templates',                   # 模板路径 - 使用相对路径
    'secret_key': 'key',                            # jwt加密的key，可以自定义
    'jwt_expire': 24*3600,                          # jwt过期时间为一天
    'MEDIA_ROOT': os.path.join(BASE_DIR, 'media'),
    'SITE_URL': 'http://127.0.0.1:8888',            # 服务器地址
    'db': {
        'host': '127.0.0.1',                        # 数据库地址
        'user': 'root',                             # 数据库用户名
        'password': 'root',                         # 数据库连接密码
        'database': 'forum',                        # 连接对应的database
        'port': 3306
    },
    'redis': {
        'host': '127.0.0.1',                        # redis数据库地址
        'password': 'redisPassword'                 # redis连接密码
    },
    'TencentSMS': {
        'sdkappid': 'your appid',                   # 发送短信服务选择腾讯，具体文档可参考官方api说明
        'appkey': 'your appkey'
    }
}

database = peewee_async.MySQLDatabase(**settings['db'])
# database = peewee_async.MySQLDatabase('message', host='127.0.0.1', port=3306, user='root', password='root')
