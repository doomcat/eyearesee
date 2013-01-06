REQUIREMENTS:
    - python 2.6+
    - latest Twisted-Python framework: `pip install twisted`
    - for now, the only database plugin is for MongoDB.
      you need 'pymongo' installed for it.
      install and run mongod. the eyearesee server will lazily create
      collections (tables) under the 'eyearesee' database when it needs
      to.
    - The two tables in the 'eyearesee' database are 'users' and 'events'.

RUNNING:
    - cd to the directory that server.py is in (the directory this README is in)
      and run server.py
    - look at config.py for values you can change.
    - by default eyearesee runs a HTTP server on port 8081. check out the
      API docs on how to register a user, then edit config.py to make that
      user an admin. boom, you have power.

