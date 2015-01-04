
# Server.py

import uuid

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import or_, and_
from tornado.concurrent import Future
from tornado.options import define, options

import json

from caravan import jobrouter

define("port", default=8888, help="run on the given port", type=int)


##### GLOBAL JOB ROUTER #####                                        
global_jobrouter = jobrouter.JobRouter()

class BaseHandler(tornado.web.RequestHandler):
    pass

class MainHandler(BaseHandler):
    def get(self):
        self.write("<h1>CARAVAN</h1>")

class ClientAPIHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, input):

        user = self.get_argument('user')
        passwd = self.get_argument('passwd')

        self.user = user

        uuid = global_jobrouter.next_db_task(user)
        if uuid:
            self.write('{"task_id": "%s"}' % uuid)
            return

        self.future = global_jobrouter.wait_for_task(user)
        task = yield self.future
        if self.request.connection.stream.closed():
            return
        
        self.write(task)

    def on_connection_close(self):
        global_jobrouter.cancel_wait(self.user, self.future)

class ClientTaskAPIHandler(BaseHandler):
    def get(self, action=''):

        user = self.get_argument('user')

        if action == 'fetch':
            t = self.get_argument('task_id')
            global_jobrouter.change_status(t, 'Fetch')
            self.write(global_jobrouter.get_task(t))

        if action == 'accept':
            t= self.get_argument('task_id')
            global_jobrouter.change_status(t,'Accept')


        self.write("")

    def post(self, action=''):
        if action == 'complete':
            t=self.get_argument('task_id')
            r=self.get_argument('result')
            global_jobrouter.change_status(t,'Complete')
            global_jobrouter.complete(t,r)
        if action == 'error':
            t=self.get_argument('task_id')
            r=self.get_argument('result')
            global_jobrouter.change_status(t,'Error')
            global_jobrouter.complete(t,r)

        self.write("")

class NewJobAPIHandler(BaseHandler):
    def post(self):
        user = self.get_argument('user')
        passwd = self.get_argument('password')
      
        task_id = global_jobrouter.new_task(self.get_argument('target'),
                                            self.get_argument('task'))
        self.write(json.dumps({"status": "ok", "target": self.get_argument('target'), "task_id": task_id}))
        self.finish()


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/1/client/(\w+)", ClientAPIHandler),
        (r"/api/1/client/task/(\w+)", ClientTaskAPIHandler),
        (r"/api/1/job/new", NewJobAPIHandler),
        
    ], debug=False)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
