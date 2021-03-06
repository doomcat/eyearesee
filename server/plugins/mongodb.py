import pymongo
import eyearelib.logger as log
import traceback
import config


__instance = None


def getInstance():
    global __instance
    if __instance is None:
        log.d("Creating a new instance of mongodb.Database")
        __instance = Database()
    return __instance


class InMemory:
    def __init__(self, mongoDB):
        log.d("Copying in-memory version of mongodb 'users' table")
        self.__database = []
        self.__users = {}
        for item in mongoDB.find():
            try:
                self.__users[item['user']] = item
                self.__database.append(item)
            except KeyError:
                pass

    def find(self, query):
        out = []
        if 'user' in query.keys()\
        and query['user'] in self.__users.keys():
            db = [self.__users[query['user']]]
        else:
            db = self.__database
        for item in db:
            skip_item = False
            for key in query.keys():
                if key not in item.keys():
                    skip_item = True
                    break
                elif item[key] != query[key]:
                    skip_item = True
                    break
            if skip_item is False:
                out.append(item)
        return out

    def set(self, query):
        # TODO finish this!
        exists = False
        for item in self.__database:
            if item['user'] == query['user']:
                item = query
                exists = True
        if exists is False:
            self.__database.append(query)

    save = set
    insert = set


class Database:
    def __init__(self):
        try:
            host = config.MONGO_HOST
        except AttributeError:
            host = 'localhost'
        try:
            port = config.MONGO_PORT
        except AttributeError:
            port = 27017
        try:
            dbname = config.MONGO_DBNAME
        except AttributeError:
            dbname = 'eyearesee'

        self.connection = pymongo.Connection(host, port)
        self.db = self.connection[dbname]
        self.users = InMemory(self.connection.eyearesee.users)
        self.events = self.connection.eyearesee.events

    def get(self, collection, query):
        if collection == 'users':
            coll = self.users
        elif collection == 'events':
            coll = self.events
        else:
            raise InvalidQuery
        try:
            output = list(coll.find(query))
            for obj in output:
                try:
                    for key in obj:
                        o = obj[key]
                        if type(o) == 'unicode':
                            obj[key] = str(o.encode('utf16', 'replace'))
                    del obj['_id']
                except:
                    pass
            return output
        except:
            log.trace()
            raise InvalidQuery

    def set(self, collection, query):
        if collection == 'users':
            coll = self.users
        elif collection == 'events':
            coll = self.events
        else:
            raise InvalidQuery
        try:
            coll.insert(query)
        except:
            log.trace()
            raise InvalidQuery

    def count(self, collection, query):
        if collection == 'users':
            return len(self.users.find(query))
        return self.events.find(query).count(True)

    def exists(self, collection, query):
        return self.count(collection, query) > 0


class InvalidQuery(Exception):
    pass
