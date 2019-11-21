from tornado.web import url
from apps.community.handler import *

urlpattern = [
    ('/groups/?', GroupHandler),
    (r'/groups/([0-9]+)/?', GroupDetailHandler),
    (r'/groups/([0-9]+)/members/?', GroupMemberHandler),
    (r'/groups/([0-9]+)/posts/?', PostHandler),
    (r'/posts/([0-9]+)/?', PostDetailHandler),

    # 评论
    (r'/posts/([0-9]+)/comments/?', PostCommentHandler),
    (r'/comments/([0-9]+)/replys/?', CommentReplyHandler),
    (r'/comments/([0-9]+)/likes/?', CommentLikeHandler),

    # 审核加入小组申请
    (r'/applys/?', ApplyHandler),
    (r'/applys/([0-9]+)/?', HandleApplyHandler),

]
