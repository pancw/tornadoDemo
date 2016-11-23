#! /usr/bin/env python
# coding=utf-8

import tornado.ioloop
import tornado.web
import motor
import uuid
import bson
import json
from tornado import gen
from tornado.options import define, options, parse_command_line
import traceback
import sys

import JsonHelper
import Logmgr

define("LoginServerPort", default=1238, help="run on the given port", type=int)

DEBUG = True


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        Logmgr.PYLOG("LoginHandler", "Get")
        self.render("template/login.html", title=u"Login")

    @gen.coroutine
    def post(self):
        try:
            db = self.settings['db']
            username = self.get_argument("u", "")
            password = self.get_argument("p", "")
            Logmgr.PYLOG("LoginHandler", {"username": username, "password": password})
            if username == '' or password == '':
                self.write(JsonHelper.failWithMessage("Empty username or password"))
                return

            res = yield db.accounts.find_one({"username": username})
            if not res or not ("password" in res) or res['password'] != password:
                self.write(JsonHelper.failWithMessage("Wrong username or password"))
                return

            new_token = str(uuid.uuid1())
            result = yield db.accounts.update({"username": username}, {'$set': {'token': new_token}})
            if result['ok'] == 1:
                respond_data = {"oid": str(res['_id']), "token": new_token}
                Logmgr.PYLOG("LoginHandler", JsonHelper.success(respond_data))
                self.write(JsonHelper.success(respond_data))
        except Exception, e:
            if DEBUG:
                print Exception, ":", e
                traceback.print_exc()
            self.write(JsonHelper.failWithMessage("Internal error."))
        finally:
            self.finish()


class RegistHandler(tornado.web.RequestHandler):

    def get(self):
        Logmgr.PYLOG("RegistHandler", "Get")
        self.render("template/regist.html", title=u"Regist")

    @gen.coroutine
    def post(self):
        try:
            db = self.settings['db']
            username = self.get_argument("u", "")
            password = self.get_argument("p", "")
            # print self.request.body
            Logmgr.PYLOG("RegistHandler", {"username": username, "password": password})
            if username == '' or password == '':
                self.write(JsonHelper.failWithMessage("Empty username or password"))
                return

            res = yield db.accounts.find_one({"username": username})
            # TODO handle db failure
            if res:
                self.write(JsonHelper.failWithMessage("Username already exists"))
                return

            new_token = str(uuid.uuid1())
            oid = bson.ObjectId()
            result = yield db.accounts.insert({"_id": oid, "username": username, "password": password, 'token': new_token})
            if result == oid:
                respond_data = {"oid": str(oid), "token": new_token}
                Logmgr.PYLOG("RegistHandler", JsonHelper.success(respond_data))
                self.write(JsonHelper.success(respond_data))
        except Exception, e:
            if DEBUG:
                print Exception, ":", e
                traceback.print_exc()
            self.write(JsonHelper.failWithMessage("Internal error."))
        finally:
            self.finish()

def main():
    client = motor.motor_tornado.MotorClient("mongodb://pancw:12345635@203.195.170.106:1238/admin")
    db = client.mygame
    application = tornado.web.Application([(r"/regist", RegistHandler),
                                           (r"/login", LoginHandler),
                                           ],
                                          db=db, autoreload=True)

    application.listen(options.LoginServerPort)
    # tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
    tornado.ioloop.IOLoop.current().start()
