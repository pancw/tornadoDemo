#! /usr/bin/env python
# coding=utf-8

import tornado.ioloop
import tornado.tcpserver
import sys
import msgpack
from tornado.options import define, options, parse_command_line

sys.path.append("utils")
sys.path.append("model")
sys.path.append("entities")

import LoginServer
import Logmgr
import db
import client
import avatar

define("MyServerPort", default=1218, help="run on the given port", type=int)
server = None

avatars = {}
def get_avatars():
	return avatars

def get_avatar(connid):
	if connid in avatars:
		return avatars[connid]
	else:
		return None

def add_avatar(connid, avatar):
	avatars[connid] = avatar

def remove_avatar(connid):
	if connid in avatars:
		avatars[connid] = None


class Connection(object):
	def __init__(self, connid, stream, address, connmgr):
		self._connid = connid  
		self._stream = stream 
		self._address = address
		self._connmgr = connmgr
		self._stream.set_close_callback(self.on_close)
		self._stream.set_nodelay(True)

		self.client = client.Client(self, self._connid)
		self.avatar = avatar.Avatar(self.client, self._connid)
		add_avatar(self._connid, self.avatar)
		self.do_read_header()
		
	def get_connid(self):
		return self._connid
		
	def reset(self):
		remove_avatar(self._connid)
		self._connid = 0
		self._stream = None
		self._address = None
		self._connmgr = None
		self.client = None
		self.avatar = None

	def do_read_header(self):
		# self._stream.read_until('z', self.handle_body)
		self._stream.read_bytes(4, self.do_read_body)

	def do_read_body(self, length):
		# Logmgr.PYLOG("Connection:do_read_body", {"length": length})
		try:
			self._stream.read_bytes(int(length), self.handle_body)
		except:
			self._stream.close()
			pass

	def handle_body(self, body):
		try:
			data = msgpack.unpackb(str(body))
			method = data[0]
			args = data[1]

			if hasattr(self.avatar, method) and callable(getattr(self.avatar, method)):
				Logmgr.PYLOG("[RPC][%s][Length:%d][id:%d]" % (str(method), len(body), self._connid), args)
				getattr(self.avatar, method)(*args)
			else:
				Logmgr.PYLOG("[RPC][调用未知函数][%s]" % str(method))
		except:
			Logmgr.PYLOG("[ERROR][%s]" % str(method), args)
			pass
		finally:
			self.do_read_header()

	def do_write(self, args):
		msg = msgpack.packb(args)
		header = str("%4d" % len(msg))
		self._stream.write(header + msg)

	def broadcast_messages(self, msg):
		for id in server.clients:
			server.clients[id].do_write(msg)

	def on_close(self):
		self._connmgr.on_client_closed(self)
		
class ConnectionMgr(tornado.tcpserver.TCPServer):
	def __init__(self):
		super(ConnectionMgr, self).__init__()
		self.curid = 0
		self.clients = {}
	
	def handle_stream(self, stream, address):
		self.curid += 1
		newconn = Connection(self.curid, stream, address, self)
		self.clients[self.curid] = newconn
		Logmgr.PYLOG("Connection", {"id": self.curid, "address": address})
		
	def on_client_closed(self, client):
		Logmgr.PYLOG("DisConnect", {"id": client.get_connid()})
		if client.get_connid() in self.clients:
			self.clients.pop(client.get_connid())
		client.reset()

def main():
	LoginServer.main()
	db.init_db()
	global server
	server = ConnectionMgr()
	server.listen(options.MyServerPort)
	Logmgr.PYLOG("Main", "server start ...")
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
