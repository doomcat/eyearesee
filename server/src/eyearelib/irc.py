import config
from eyearelib import logger, database, handler
from eyearelib.events import event
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
	versionName = 'eyearesee'
	versionNum = '0.1'
	sourceUrl = 'https://github.com/doomcat/eyearesee'

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

	def _event(self,type,user=0,server=0,
		channel=None,nicks=None,data=None,master=True):
		if user == 0:
			user = self.user
		if server == 0:
			server = self.server

		event(
			connection=self,
			type=type,
			user=user,
			server=server,
			nicks=nicks,
			data=data,
			master=master
		)

	def signedOn(self):
		uid = "%s$%s" % (self.user,self.server)
		self.pool['connections'][uid] = self

		self._event(
			type=handler.CONNECTED,
			nicks=[self.nickname],
			master=True
		)

		join(self.user,self.server,'#eyearesee')

	def joined(self, channel):
		channels = self.pool['channels']
		cid = "%s$%s" % (self.server, channel)
		
		self._joinedChannel(channel)

		self._event(
			type=handler.JOINED,
			nicks=[self.nickname],
			channel=channel
		)

		logger.d("channels[%s] = %s",cid, channels[cid])

	def left(self, channel):
		self._leftChannel(channel)

		self._event(
			type=handler.LEFT,
			nicks=[self.nickname],
			channel=channel
		)

	def kickedFrom(self, channel, kicker, message):
		self.userKicked(self.nickname, channel, kicker, message)

	def privmsg(self, nick, channel, msg):
		channels = self.pool['channels']
		cid = "%s$%s" % (self.server, channel)

		self._makeMaster(channels[cid])

		if msg.startswith('/me '):
			type=handler.ACTION
			msg=msg[3:]
		else:
			type=handler.MESSAGE

		self._event(
			type=type,
			channel=channel,
			nicks=[nick],
			data=msg,
			master=self._isMaster(channels[cid])
		)
		
	def action(self, nick, channel, msg):
		self.privmsg(nick, channel, "/me "+msg)

	def nickChanged(self, nick):
		self._event(
			type=handler.RENAMED,
			nicks=[self.nickname, nick]
		)

	def userJoined(self, nick, channel):
		c = self.pool['channels']["%s$%s" % (self.server, channel)]
		self._event(
			type=handler.JOINED,
			channel=channel,
			nicks=[nick],
			master=self._isMaster(c)
		)

	def userLeft(self, nick, channel):
		c = self.pool['channels']["%s$%s" % (self.server, channel)]
		self._event(
			type=handler.LEFT,
			channel=channel,
			nicks=[nick],
			master=self._isMaster(c)
		)

	def userKicked(self, kickee, channel, kicker, message):
		c = self.pool['channels']["%s$%s" % (self.server, channel)]
		self._event(
			type=handler.KICKED,
			channel=channel,
			nicks=[kicker,kickee],
			data=message,
			master=self._isMaster(c)
		)
		if kickee == self.nickname:
			self._leftChannel(channel)

	def userQuit(self, nick, channel, message):
		self._event(
			type=handler.QUIT,
			nicks=[nick],
			data=message
		)

	def topicUpdated(self, nick, channel, newTopic):
		c = self.pool['channels']["%s$%s" % (self.server, channel)]
		self._event(
			type=handler.TOPIC,
			channel=channel,
			nicks=[nick],
			data=newTopic,
			master=self._isMaster(c)
		)

	def userRenamed(self, oldName, newName):
		self._event(
			type=handler.TOPIC,
			nicks=[oldName,newName]
		)

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
		connector._event(
			type=handler.LOST_CONNECTION,
			channel=None,
			nicks=[self.nickname],
			data=reason
		)
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		connector._event(
			type=handler.FAILED_CONNECTION,
			channel=None,
			nicks=[self.nickname],
			data=reason
		)
		connector._delMasterAll()

def test():
	event(None, "test","owain","localhost","null",
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

