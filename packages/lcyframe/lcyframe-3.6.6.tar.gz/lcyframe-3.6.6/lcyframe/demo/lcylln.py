# -*- coding:utf-8 -*-
import json
import tornado.httpserver
import tornado.ioloop
from tornado.web import RequestHandler, Application
import tornado.options
from tornado.options import define, options
from tornado.escape import json_decode, json_encode

define("port", default=6677, help="run on the gevent port", type=int)
define("host", default="127.0.0.1", help="host aaa", type=str)


class ReverseHandler(RequestHandler):
    def get(self, word):
        self.write(word[::-1])

from lcyframe.base import BaseHandler
class IndexHandler(RequestHandler):
    def get(self):
        # req = self.request.body
        # print("type(req)：",type(req))
        # req_de = json_decode(req)
        # print("type(req_de)：",type(req_de))
        ret = {"a": "是的是的所", "error": 1, "msg": "msg", }

        ret = json.dumps(ret, ensure_ascii=False)
        self.write(ret)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application(
        handlers=[
            (r"/reverse/(\w+)", ReverseHandler),
            (r"/demo", IndexHandler),
        ],
        debug=True,
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print('running: %s' % options.port)
    tornado.ioloop.IOLoop.instance().start()