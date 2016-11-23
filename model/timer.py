#! /usr/bin/env python
# coding=utf-8

import time
import datetime

def get_now():
    return time.time()

def get_date():
    return datetime.datetime.now()

def get_strnow():
    return time.strftime("%Y-%m-%d %H:%I:%S", time.localtime(time.time()))
