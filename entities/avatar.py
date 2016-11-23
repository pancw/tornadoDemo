#! /usr/bin/env python
# coding=utf-8

import inspect

class Avatar(object):
    def __init__(self, client, connid):
        self.client = client
        self.connid = connid

    def login(self, username, oid, token):
        self.client.login_ok("ok", (1,2,3,4,5), {"x":1, "y":2})