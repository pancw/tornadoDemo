#! /usr/bin/env python
# coding=utf-8

import Logmgr

class Client(object):
    def __init__(self, Connection, connid):
        self.connect = Connection
        self.connid = connid

    def __getattr__(self, method_name):
        def caller(*args):
            Logmgr.PYLOG("[Write][%s]" % (str(method_name)), args)
            self.connect.do_write([method_name, args])
        return caller
