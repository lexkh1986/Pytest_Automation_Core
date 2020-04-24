from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from core.abstract.BaseFactory import BaseFactory


class DBApi(object):
    """
    Data abstract interface class defines a database api connector
    """

    def __init__(self, name, type):
        self.name = name
        self.type = type


class Server(object):
    """
    Data abstract interface class defines a database server
    """
    conApi = None

    def __init__(self, dialect, ip, port=3306):
        self.dialect = dialect
        self.ip = ip
        self.port = port


class DataBase(object):
    """
    Data abstract interface class defines a database
    """
    server = None

    def __init__(self, dbName):
        self.dbName = dbName


class DBUser(object):
    """
    Data abstract interface class defines a user of database
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password


class DataFactory(BaseFactory):
    """
    Object inherited class defines a POM structure simulate a database system to test
    DataFactory object holds:
    - An attached SqlAlchemy engine to produce & control db connection tests (inherited Session class)
    @author: lex.khuat
    """

    # ------ Public methods -------
    def addDBApi(self, name, type):
        """
        Store a driver api to connect to database
        Follow: https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.Engine
        @param name: name of driver api
        @param type: type of database
        @return: self
        """
        newApi = DBApi(name, type)
        for item in self.getObj(Server):
            setattr(item, 'conApi', newApi)
        return self.storeObj(name, newApi, DBApi)

    def addServer(self, svName: str, svObj: Server):
        """
        Store a server details
        @param svName: server name/alias to store
        @param svObj: server object
        @return: self
        """
        for item in self.getObj(DBApi):
            if item.type == svObj.dialect:
                svObj.__setattr__('conApi', item)
        return self.storeObj(svName, svObj, Server)

    def addDatabase(self, svName: str, dbObj: DataBase):
        """
        Store a database details
        @param svName: name of server to store db
        @param dbObj: database object
        @return: self
        """
        if not isinstance(dbObj, DataBase):
            raise ValueError('%s must be %s classtype' % (dbObj, DataBase))
        for key, val in self.__dict__.items():
            if key == svName:
                if not isinstance(val, Server):
                    raise LookupError('%s is not a server classtype' % key)
                else:
                    dbObj.server = val
                    val.__setattr__(dbObj.dbName, dbObj)
                    self.storeObj(dbObj.dbName, dbObj, DataBase)
                    return self
        return self

    def addUser(self, userObj: DBUser):
        """
        Store a db user
        @param userObj: dbuser object
        @return: self
        """
        return self.storeObj(userObj.username, userObj, DBUser)

    def storedServer(self):
        """
        Return all stored DB servers
        @return: <List>Server
        """
        return self.getObj(Server)

    def storedDatabases(self):
        """
        Return all stored DB databases
        @return: <List>Database
        """
        return self.getObj(DataBase)

    def storedUsers(self):
        """
        Return all stored DB users
        @return: <List>DBUser
        """
        return self.getObj(DBUser)

    def storedEngines(self):
        """
        Return all stored db engine
        @return: <List>Engine
        """
        return self.getObj(Engine)

    def storedAPIs(self):
        """
        Return all stored db connection api
        @return: <List>DBApi
        """
        return self.getObj(DBApi)

    storedServers = property(storedServer)
    storedDatabases = property(storedDatabases)
    storedUsers = property(storedUsers)
    storedEngines = property(storedEngines)
    storedAPIs = property(storedAPIs)

    def buildEngine(self, name: str, database: DataBase, user: DBUser, **kwargs):
        """
        Build a new engine to work with database
        @param name: name the new engine
        @param database: database to connect, must be stored in factory first
        @param user: user to connect, must be stored in factory first
        @param kwargs: more keyword args from https://docs.sqlalchemy.org/en/13/core/engines.html
        @return: <Engine> newEngine
        """
        if not isinstance(database, DataBase):
            raise ValueError('%s must be %s classtype' % (database, DataBase))
        if not isinstance(user, DBUser):
            raise ValueError('%s must be %s classtype' % (user, DBUser))
        if database not in self.storedDatabases:
            raise LookupError('%s is not stored in factory' % database.dbName)
        if user not in self.storedUsers:
            raise LookupError('%s is not stored in factory' % user.username)
        conStr = '{}{}://{}:{}@{}:{}/{}'.format(
            database.server.dialect,
            '' if database.server.conApi.name is None else '+%s' % database.server.conApi.name,
            user.username,
            user.password,
            database.server.ip,
            database.server.port,
            database.dbName)
        newEngine = create_engine(conStr, **kwargs)
        self.__setattr__(name, newEngine)
        return newEngine

    @contextmanager
    def dbapi_connect(self, engine: Engine):
        """
        Perform a connection using dbapi driver (support call proc & multi table results)
        Can use by "with" block which yield connection, cursor with safe closing
        @param engine: <Engine>db engine
        """
        connection = engine.raw_connection()
        cursor = connection.cursor()
        try:
            yield connection, cursor
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e)
        finally:
            connection.close()

    @contextmanager
    def connect(self, engine: Engine):
        """
        Perform a connection using sqlalchemy connection pool (support sqlalchemy execution methods)
        Can use by "with" block which yield connection and safe closing
        @param engine: <Engine>db engine
        """
        connection = engine.connect()
        try:
            yield connection
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e)
        finally:
            connection.close()

    @contextmanager
    def begin_trans(self, connection):
        """
        Perform a safe transaction insert/update into database through a connection
        Rollback if found database exception
        @param connection: connection to start transaction
        """
        transaction = connection.begin()
        try:
            yield transaction
        except SQLAlchemyError as e:
            print('Caught SQLAlchemyError and rolledback transaction: {}'.format(e))
            transaction.rollback()


if __name__ == '__main__':
    df = DataFactory()
    df.addDBApi('pymysql', 'mysql')
    df.addUser(DBUser('fps', 'fps'))
    df.addServer('slave', Server('mysql', '10.18.200.72', 3306))
    df.addDatabase('slave', DataBase('DCS_DataCenter'))
    df.addDatabase('slave', DataBase('CTS_DataCenter'))
    df.addServer('master2', Server('mysql', '10.18.200.70', 3306))
    df.addDatabase('master2', DataBase('DCS_RawTransaction'))