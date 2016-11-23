#! /usr/bin/env python
# coding=utf-8

import timer

def PYLOG(modules, args):
    print ("[" + str(timer.get_strnow()) + "]" + "[" + str(modules) + "]" + str(args))
