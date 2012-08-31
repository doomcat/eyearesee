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
	channels = set()

	def _joinedChannel(self,channel):
		channels = self.pool['channels']	
		cid = "%s$%s" % (self.server, channel)
		if cid in channels.keys():
			channels[cid][self.user] = self
		else:
			channels[cid] = {self.user: self}
		self._makeMaster(channels[cid])
		self.channels.add(channel)

	def _makeMaster(self,channelObj):
		if 'master' not in channelObj.keys()\
		or channelObj['master'] == None:
			logger.d("Made %s master for %s",self,channelObj)
			channelObj['master'] = self

	def _makeMasterAll(self):
		for channel in self.channels:
			cid = "%s$%s" % (self.server, channel)
			if cid in self.pool['channels'].keys():
				self._makeMaster(self.pool['channels'][cid])

	def _delMaster(self,channelObj):
		if 'master' in channelObj.keys():
			logger.d("Removed master for %s",channelObj)
			channelObj['master'] = None

	def _delMasterAll(self):
		for channel in self.channels:
			cid = "%s$%s" % (self.server, channel)
			if cid in self.pool['channels'].keys():
				self._delMaster(self.pool['channels'][cid])

	def _leftChannel(self,channel):
		channels = self.pool['channels']
		cid = "%s$%s" % (self.server, channel)
		if cid not in channels.keys(): return
		self._delMaster(channels[cid])
		self.channels.remove(channel)

	def _isMaster(self,channelObj):
		if 'master' not in channelObj.keys(): return False
		return channelObj['master'] == self

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
		
		self._joinedChannel(channel)
		events.event(self,handler.JOINED,
			self.user,self.server,channel,
			None,None,self._isMaster(channels[cid]))

		logger.d("channels[%s] = %s",cid, channels[cid])

	def privmsg(self, nick, channel, msg):
		channels = self.pool['channels']
		cid = "%s$%s" % (self.server, channel)

		self._makeMaster(channels[cid])
		if (channel[0] not in ['#','&']): user = self.user
		else: user = None
		events.event(self,handler.MESSAGE,
			user,self.server,channel,
			[nick], msg,self._isMaster(channels[cid]))

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

