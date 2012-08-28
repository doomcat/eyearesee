import config
from eyearelib import logger, database, events, handler
from twisted.internet.task import LoopingCall
import twisted.words.protocols.irc
from twisted.internet import protocol, reactor
import json

pool = {
	"connections": {},
	"channels": {}
}

class UserNotConnected(Exception):
	pass

class IRCConnection(twisted.words.protocols.irc.IRCClient):
	def _get_nickname(self):
		return self.factory.nickname
	def _get_user(self):
		return self.factory.user
	def _get_server(self):
		return self.factory.server
	def _get_pool(self):
		global pool
		return pool
	nickname = property(_get_nickname)
	user = property(_get_user)
	server = property(_get_server)
	pool = property(_get_pool)

	def signedOn(self):
		uid = "%s$%s" % (self.user,self.server)
		self.pool['connections'][uid] = self

		events.event(self,handler.CONNECTED,
			self.user,self.server,
			None,[self.nickname],None)

		join(self.user,self.server,'#eyearesee')

	def joined(self, channel):
		channels = self.pool['channels']
		cid = "%s$%s" % (self.server, channel)
		if cid in channels.keys():
			channels[cid][self.user] = self
		else:
			channels[cid] = {self.user: self}

		events.event(self,handler.JOINED,
			self.user,self.server,channel,
			None,None)

		logger.d("channels[%s] = %s",cid, channels[cid])

	def privmsg(self, nick, channel, msg):
		events.event(self,handler.MESSAGE,
			self.user,self.server,channel,
			[nick], msg)

class IRCConnectionFactory(protocol.ClientFactory):

	def __init__(self, user, server):
		self.user = user
		self.nickname = user
		self.server = server

	def buildProtocol(self, addr):
		p = IRCConnection()
		p.factory = self
		return p

	def clientConnectionLost(self, connector, reason):
		events.event(connector, handler.LOST_CONNECTION,
			self.user, self.server, None, [self.nickname], reason)
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		events.event(connector, handler.FAILED_CONNECTION,
			self.user, self.server, None, [self.nickname], reason)

def test():
	events.event(None, "test","owain","localhost","null",
		["erinaceous"], "test event")

def connect(user,server):
	global pool
	connections = pool['connections']
	id = "%s$%s" % (user,server)
	if id not in connections.keys():
		addr,port = server.split(':')
		logger.d("Connecting to %s, port %s as %s",addr,port,user)
		connections[id] = reactor.connectTCP(addr, int(port),
			IRCConnectionFactory(user, server))

def join(user,server,channel):
	#global __channels, __connections
	global pool
	channels = pool['channels']
	connections = pool['connections']
	uid = "%s$%s" % (user,server)
	cid = "%s$%s" % (server,channel)
	if uid not in connections.keys():
		raise UserNotConnected
	if cid not in channels.keys() and channel[0]=='#':
		connections[uid].join(channel)

def getConnection(user,server):
	global pool
	connections = pool['connections']
	id = "%s$%s" % (user,server)
	if id in connections.keys():
		return connections[id]
	else:
		raise UserNotConnected

