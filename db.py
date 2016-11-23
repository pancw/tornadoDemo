#! /usr/bin/env python
# coding=utf-8

import motor
db = None

def init_db():
    global db
    client = motor.motor_tornado.MotorClient("mongodb://pancw:12345635@203.195.170.106:1238/admin")
    db = client.mygame

def get_db():
    global db
    return db
