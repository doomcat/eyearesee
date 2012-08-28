import eyearelib.logger
LOG_LEVEL=eyearelib.logger.DEBUG

URL="https://eyearesee.in"
HOSTNAME="eyearesee.in"
HTTP_ADDRESS="0.0.0.0"
HTTP_PORT=8081

ADMINS=["owain"]
READ_ONLY=["eyearesee"]

import eyearelib.handler, plugins.funkyhandler
EVENT_HANDLERS=[
	eyearelib.handler,
	plugins.funkyhandler,
]

import plugins.mongodb
DATABASE_HANDLER=plugins.mongodb
