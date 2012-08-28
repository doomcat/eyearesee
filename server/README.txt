REQUIREMENTS:
	- python 2.6+. personally I'm using PyPy instead of CPython.
	  (if you're using normal python instead of pypy, edit the top line of
	   `server/eyearesee` to read
	   #!/usr/bin/python -OO
	   instead of
	   #!/usr/bin/pypy)
	- latest Twisted-Python framework: `pip install twisted`
	- for now, the only database plugin is for MongoDB.
	  install and run mongod. the eyearesee server will lazily create
	  collections (tables) under the 'eyearesee' database when it needs
	  to.

RUNNING:
	- you can run it directly from the src/ folder. but I hate how .pyc
	  and .pyo files fill that up when you run it directly from src/, so
	  run `./src/compile` and that will generate a .zip containing the
	  "compiled" python sources and then you can run `server/eyearesee`.
	- look at config.py for values you can change.
	- by default eyearesee runs a HTTP server on port 8081. check out the
	  API docs on how to register a user, then edit config.py to make that
	  user an admin. boom, you have power.

