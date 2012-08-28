eyearesee - the IRC to HTTP bridge that makes it easier to idle in channels
from wherever you are
------------------------------------------------------------------------------
written in python, using the twisted framework.
github.com/doomcat/eyearesee
try out the demo server at https://eyearesee.in
written & maintained by owain jones <owain@slashingedge.co.uk>
------------------------------------------------------------------------------

0.	CONTENTS
1.1 Server specification
1.2 Object/database schema
1.3 RESTFUL API documentation
2.  Configuration
3.  Bugs/issues


1.1	SERVER SPECIFICATION
------------------------------------------------------------------------------
eyearesee acts as a multi-user daemon, handling multiple IRC connections for
multiple users. when talking about 'users' in eyearesee, we actually mean the
user accounts, which can own multiple connections to IRC servers each. this is
different to 'nicks', which would be a single connection to an IRC channel.

eyearesee acts as a buffer between the IRC server(s) and you - it keeps a
persistent connection to your servers and channels, like having an IRC client
in a screen session on a remote server. messages received are logged
indefinitely in a database (said database is dependent on what plugins are
loaded; the default database is 'memory' e.g. simply kept in RAM), and the
user can fetch new (or old) messages by querying the server via HTTP POST and
GET requests.

requests and commands are sent to the server via HTTP, with different URLs for
different functionality (/server, /channel, etc.) - and the server responds
with data serialized into JSON. the server can either be polled, or hold a
connection open until new data (messages in a channel) appears. this means the
clients using eyearesee can use IRC on flakey (mobile) connections, and do
stuff like periodically poll for 'notifications' - making it feasible to use
IRC on mobile devices where battery/data usage are issues.

the data from channels is shared; one connection is kept as a 'master'
connection, from which received messages are stored into the database. the
other user's connections to the same channel are kept open, but used only for
commands and sending messages.
(when talking to other nicks via private chat or DCC, the
connections won't (can't) be shared)


1.2	OBJECTS/DATABASE SCHEMA
------------------------------------------------------------------------------
central to the whole app is the 'event' object. in JSON format, it looks like
this:
{
	"timestamp":	xxxxxxxxxx.xx,
	"event":	"message",
	"nicks":	["eyerobot!host.name.of.client",...],
	"server":	"irc.aberwiki.org",
	"channel":	"#eyearesee",
	"data":		"The message or data that actually got sent"
}
where 'timestamp' is the time, in seconds since the unix epoch, with
millisecond precision.
'nicks' is a list for events which can involve multiple nicks, e.g. someone
performing a mass op/de-op in a channel, or multiple people being kicked.

every reply the server gives is laid out like this:
{
	"status":	1,
	"server_time":	xxxxxxxxxx.xx,
	"payload":	[
		{ event },
		{ event },
		...
	]
}
where "status" is the status of the request. '1' indicates the request is
fine. '0' indicates no data, and any other code means an error occurred.
"server_time" is the current time of the server, as unix epoch (milli)seconds.
(this allows you to syncronize times between clients and server for
example, so you can get accurate timestamps for channel messages)
assuming the request is fine, the "payload" will be a list of events, usually.
unless the request is write-only or isn't intended to send any data to the
client, in which case payload will be omitted.

since these objects are so generic, different usage patterns will use
different properties. properties that are empty or not appropriate for that
query will be omitted from the output.

the database layout looks like this:
 + (root)
 |
 | users
 |      \
 |       owain
 |            \
 |             | token: werfgti44tfijo2f3243f4
 |             | hash: 6b3a55e0261b0304143f805...
 |             | permissions: ADMIN|WRITE|LOGIN
 |             | servers
 |                      \
 |                       | irc.aberwiki.org
 |                                         \
 |                                          | channels: [#eyearesee, eyerobot]
 |                                          | nick: Erinaceous
 |                                          | ignore: [nick1, nick2, ...]
 |
 | channels
 |         \
 |          | #eyearesee
 |          |            \
 |          |             | server: irc.aberwiki.org
 |          |             | topic: "eyearesee.in | Testing and stuff"
 |          |             | nicks: [owain, ted, eyerobot, ...]
 |          |             | events: [{event}, {event}, ...]
 |          |
 |          | owain$eyerobot
 |          |                \
 |          |                 | server: irc.aberwiki.org
 |          |                 | nicks: [owain, eyerobot]
 |          |                 | events: [...]

the actual connections to the IRC servers are transient (only exist whilst the
program is running, and are subject to disconnection), they are seperated from
the rest of the database. they are kept in a pool:

 + (root)
 |
 | channels
 |         \
 |          | #eyearesee
 |          |           \
 |          |            | server: irc.aberwiki.org
 |          |            | connections: [{connection}, {connection}]
 |          |
 |          | #42
 |          |    \
 |          |     | server: irc.aberwiki.org
 |          |     | connections: [{connection}]
 | 
 | servers
 |        \
 |         | irc.aberwiki.org
 |         |                 \
 |         |                  | connections: [{connection}, {connection}]
 |
 | connections: [{connection}, {connection}]

where the 'connection' objects are owned by different users. the first
connection in the list for every channel becomes the 'master' - events
received from IRC on this connection are saved to the database. events
received for the channel from the other connections are ignored.

connection objects contain a 'user' property that indicate what user each
individual connection belongs to.

1.3	RESTFUL API specification
------------------------------------------------------------------------------
requests are standard HTTP GET/POST requests - the server accepts either. this
makes it easy to get data from the server using browser javascript frameworks
(i.e. jQuery) or craft requests for stuff like `curl` or `wget`.

users must provide an 'auth token' as a field for every request. this token
is generated by the server when the user requests authentication. 

what fields are required from the client differs between the different kinds
of request, but at minimum the following fields are needed:
 - user			the account of the eyearesee user that is making this 
			request
 - token 		the 'auth token' given to that user by the server.

other generic fields:
 - servers		the IRC server this request/command is related to
 - channels	   	   " "  channel 		" "
 - since		timestamp in epoch seconds, declaring when we last
			made a request. used for getting the newest
			'unread' events, usually.
 - before		timestamp in seconds, for when you want to get events
			that happened before a certain time.
 - limit		maximum number of objects the server should send back.
 - ignore		ignore events involving anyone from a list of nicks
			(delimited with a comma, e.g. "ignore=owain,ted")
 - filter		ignore events for which a regular expression is true.
			(e.g. "/.*\.jpg$/" - ignore messages that end in .jpg)
 - highlight		get only events whose data matches true for a regular
			expression.
 - nicks		get only events/apply command to, a list of nicks
			(delimited with a comma)
 - data			if the request involves further data (e.g. changing
			your nick, sending a message, joining a channel)
			pass it in this field.

api URLS:
/connect		connect to the server specified in $server.
/disconnect		disconnect to the server specified in $server.
/join			connect to the $channel on $server.
/part			leave the $channel on $server
/register		register $user on the eyearesee server instance, with
			the password defined in $data.
/auth			authenticate with the server - send a sha-256 hash of
			user's password in $data. server will respond with
			{ ... "payload": ["TOKEN"] ... }, where TOKEN is
			another hash generated by the server. after doing this
			request, all your consecutive requests have to have
			TOKEN passed in $token.
/message		send a message (specified in $data) in $channel
			on $server as $user.
/action			perform an action ("/me does something") in $channel
			on $server as $user.
/permissions		change permissions of $nicks in $channel to the
			permissions described in $data (e.g. +o for op)
/kick			kick the nicks described in $nicks from $channel with
			the optional message defined in $data.
/events			get events. filter the list of objects using channels,
			since/before, ignore/highlight, etc.
/admin			perform admin stuff (reload configs, reload classes,
			register/unregister plugins, remove/ban users). $data
			is a JSON-encoded object describing what you want to
			do. not really part of the API per se.
