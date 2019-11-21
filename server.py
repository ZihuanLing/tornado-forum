from tornado.web import Application
from tornado.ioloop import IOLoop

from MxForum.urls import urlpattern
from MxForum.settings import settings, database
from peewee_async import Manager


if __name__ == '__main__':
    # 集成json到wtforms
    import wtforms_json
    wtforms_json.init()

    app = Application(urlpattern, debug=True, **settings)
    app.listen(8888)

    database.set_allow_sync(False)
    objects = Manager(database)

    app.objects = objects

    io_loop = IOLoop()
    io_loop.current().start()
    print('Server started.')
