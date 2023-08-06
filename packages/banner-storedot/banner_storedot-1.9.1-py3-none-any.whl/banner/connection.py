
from typing import Union, Dict, Iterable
from abc import ABC, abstractmethod
from enum import Enum
from itertools import chain
from json import loads, dumps
from inspect import getfullargspec

from MySQLdb import connect as mysql_connect, MySQLError
from MySQLdb._exceptions import OperationalError
from MySQLdb.cursors import DictCursor

from psycopg2 import connect as postgres_sql_connect, Error as PostgresSQLError
from psycopg2.extras import RealDictCursor
from psycopg2.errors import DatabaseError as PostgresSQLDatabaseError
import redis
from pandas import DataFrame, concat
from numpy import int64

from banner.utils.const import TTL_KWARG
from banner.utils.misc import digested_key #Banner

class ConnectionType(Enum):
    mysql = 'mysql'
    redis = 'redis'
    postgres = 'postgres'

class ConnectionFactory(object):
    ''' Connection Factory'''
    def __new__(self, con_type: Union[ConnectionType, str] = ConnectionType.mysql, **kwargs):
        try:
            con_type = ConnectionType[con_type]

        except KeyError:
            pass
            
        if not isinstance(con_type, ConnectionType):
            raise TypeError('Unknown Connection Type')
        
        if con_type is ConnectionType.redis:
            return RedisConnection(**kwargs)
            
        return MySqlConnection(**kwargs)        

class Connection(ABC):
    @abstractmethod
    def retrieve(self, query: str):
        pass

class RelationalConnection(Connection):
    @abstractmethod
    def describe(self, table: str = ''):
        pass

class Storage(Connection):
    @abstractmethod
    def store(self, key, value):
        pass

    @abstractmethod
    def keys(self, query):
        pass

class PrintableConnection(Connection):
    @abstractmethod
    def name(self):
        pass
    
    @abstractmethod
    def __str__(self):
        pass

class RedisConnection(Storage, PrintableConnection):
    HOUR = 3600

    def __init__(self, host, port=6379, passwd=None, db=0, ssl_key=None, ssl_cert=None, name=None, ttl=HOUR):
        self.data = dict(
            host=host,
            port=port,
            password=passwd,
            db=db,
            ssl_keyfile=ssl_key,
            ssl_certfile=ssl_cert,
        )

        self.__ttl = ttl or RedisConnection.HOUR
        self.__name = name

        # Redis manages opening/closing by itself, it is safe to init it here
        self.instance = redis.Redis(
            **self.data, 
            decode_responses=True
        )
    
    def keys(self, query: str):
        '''
            Retrieve Keys from Storage
        '''
        return self.instance.keys(pattern=f'{str(query)}')

    def retrieve(self, func: callable, *args, **kwargs):
        '''
            Retrieve Value from Storage
        '''
        controller = QUERY_TO_STORAGE_CONTROL.get(func.__name__, DefaultStorageController)

        return controller.retrieve(
            self.instance, func, *args, **kwargs
        )
        
    def store(self, value, func: callable, *args, ttl=None, nx=True, **kwargs):
        '''
            Set Value Into Storage
        '''
        ttl = ttl if ttl else self.__ttl

        controller = QUERY_TO_STORAGE_CONTROL.get(func.__name__, DefaultStorageController)
        
        return controller.store(
            self.instance, value, func, *args, ttl=ttl, nx=nx, **kwargs
        )
        
    @property
    def name(self):
        return self.__name or str(self.data)

    def __str__(self):
        return self.name
            
class MySqlConnection(RelationalConnection, PrintableConnection):
    def __init__(self, host, user, passwd=None, db=None, ssl_key=None, ssl_cert=None, charset='utf8', use_unicode=True, name=None):
        self.data = dict(
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            ssl=dict(key=ssl_key, cert=ssl_cert),
            charset=charset,
            use_unicode=use_unicode,
            cursorclass=DictCursor
        )

        self.__name = name

    def retrieve(self, query: str):
        try:
            instance = self.__connect()
            
            cursor = instance.cursor()
            
            cursor.execute(query)

            records = cursor.fetchall()

            cursor.close()
        
            records = DataFrame(records).convert_dtypes()
            
        except MySQLError as e:
            raise e
        
        finally:
            self.__close(instance)        

        return records

    def describe(self, table: str = ''):
        _query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.data.get('db')}'"

        if table:
            _query = f'DESCRIBE {table}'

        return self.retrieve(_query)

    def __connect(self):
        try:
            return mysql_connect(**self.data)

        except OperationalError:
            raise MySQLError(
                f'Connection to {self.name} Failed'
            )
      
    def __close(self, instance):
        try:
            instance.close() 
            
        except (AttributeError, MySQLError):
            pass
    
    @property
    def name(self):
        return self.__name or str(self.data)

    def __str__(self):
        return self.name

class PostgresSqlConnection(RelationalConnection, PrintableConnection):
    def __init__(self, host, user, port=5432, passwd=None, db=None, ssl_key=None, ssl_cert=None, charset='utf8', name=None):
        self.data = dict(
            host=host,
            user=user,
            password=passwd,
            dbname=db,
            sslkey=ssl_key,
            sslcert=ssl_cert
        )

        self.__name = name
        self.__charset = charset
        
    def retrieve(self, query: str):
        try:
            instance = self.__connect()
            
            cursor = instance.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(query)
            
            records = cursor.fetchall()
            
            cursor.close()
        
            records = DataFrame(records).convert_dtypes()

        except PostgresSQLError as e:
            raise e
        
        finally:
            self.__close(instance)        

        return records

    def describe(self, table: str = ''):
        _query = f"SELECT table_name FROM information_schema.tables"

        if table:
            _query = (
                'SELECT column_name as "Field", data_type as "Type", is_nullable as "Null", column_default as "Default"'
                f" FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table}'"
            )
            
        return self.retrieve(_query)
    
    def __connect(self):
        try:
            instance = postgres_sql_connect(**self.data)
            instance.set_client_encoding(self.__charset)

            return instance

        except PostgresSQLError:
            raise PostgresSQLDatabaseError(
                f'Connection to {self.name} Failed'
            )
      
    def __close(self, instance):
        try:
            instance.close() 
            
        except (AttributeError, PostgresSQLError):
            pass

    @property
    def name(self):
        return self.__name or str(self.data)

    def __str__(self):
        return self.name

class StorageController(ABC):
    '''
        Handles Store&Retrieve from Data Storage
    '''
    @abstractmethod
    def store(): # Return Command to fetch the data
        pass

    @abstractmethod
    def retrieve(): # Return Command to fetch the data
        pass

class DefaultStorageController(StorageController):
    '''
        Default Storage Controller
    '''
    NUM_OF_KEYS = 10
    MAX_ROWS = 100000

    @staticmethod
    def __table_index(func: callable, *args, **kwargs):
        try:
            table_index = getfullargspec(func).args.index('table')
            
        except (IndexError, KeyError, ValueError):
            table_index = -1
        
        return table_index

    @staticmethod
    def __keys(func: callable, *args, **kwargs):
        key = digested_key(func, *args, **kwargs)

        keys = [f'{key}#{i}' for i in range(DefaultStorageController.NUM_OF_KEYS)]

        return keys

    @staticmethod
    def store(
        storage: Union[redis.client.Redis], value: DataFrame, 
        func: callable, *args, 
        ttl=None, nx=True, **kwargs
    ):  
        keys = DefaultStorageController.__keys(func, *args, **kwargs)
        values = value.split(size=DefaultStorageController.MAX_ROWS) # This is a banner function
        
        for key, val in zip(keys, values):
            resp = storage.set(
                key, val.to_json(orient='records'), ex=ttl, nx=nx
            )

            if not resp:
                raise redis.ResponseError
            
        return True

    @staticmethod
    def retrieve(
        storage: Union[redis.client.Redis], func: callable, *args, **kwargs
    ):
        keys = DefaultStorageController.__keys(func, *args, **kwargs)
        values = list(filter(None, storage.mget(keys)))

        table_index = DefaultStorageController.__table_index(func) # Is it a table query?

        df = DataFrame.from_dict(
            chain(*[loads(value) for value in values]), orient='columns'
        ).convert_dtypes()
        
        if table_index >= 0:
            df._tables = [args[table_index]] # Set table metadata

        return df

class NewareCacheController(DefaultStorageController):
    '''
        Neware Cache Data(DataFrame) Storage Controller
    '''
    PRIMARY_KEY = ['ip', 'dev_uid', 'unit_id', 'chl_id', 'test_id']

    @staticmethod
    def __keys(func: callable, *args, **kwargs):
        _keys_index = NewareCacheController.__keys_index(func, *args, **kwargs)
        
        try:
            assert(_keys_index >= 0)
            
            if (all(isinstance(item, Iterable) for item in args[_keys_index])):
                _keys = [tuple(key) for key in args[_keys_index]] # Make sure each key(collection) is a tuple
            
            else:
                _keys = [tuple(args[_keys_index])] # Single entry was given
            
            return [
                f'{ip}-{device}-{unit}-{channel}-{test}' for ip, device, unit, channel, test in _keys
            ]
                
        except (AssertionError, TypeError):
            return digested_key(func, *args, **kwargs)
    
    @staticmethod
    def __keys_index(func: callable, *args, **kwargs):
        try:
            keys_index = getfullargspec(func).args.index('keys')

        except (IndexError, KeyError, ValueError):
            keys_index = -1

        return keys_index

    @staticmethod
    def __dump(df: DataFrame):
        df_without_pk = df[df.columns.difference(NewareCacheController.PRIMARY_KEY)]

        return {
            str(key): loads(value.to_json(orient='values')) for key, value in df_without_pk.items()
        }

    @staticmethod
    def __load(key: str, value: dict):
        df = DataFrame.from_dict(value)
        
        for pk, val in zip(reversed(NewareCacheController.PRIMARY_KEY), reversed(key.split('-'))):
            df.insert(0, pk, val)
        
        return df

    @staticmethod
    def store(
        storage: Union[redis.client.Redis], value: DataFrame, 
        func: callable, *args, 
        ttl=None, nx=True, **kwargs
    ):  
        try: 
            data = value.groupby(NewareCacheController.PRIMARY_KEY).apply(NewareCacheController.__dump)
            
            for key, val in data.items():
                _key = '-'.join(map(str, key))
                
                resp = storage.json().set(
                    _key, '$', val, nx=nx
                )
                
                if resp:
                    storage.expire(_key, ttl)
                
            return True

        except (TypeError, KeyError, redis.ResponseError):
            raise ValueError(f'Bad Input')
        
    @staticmethod
    def retrieve(
        storage: Union[redis.client.Redis], func: callable, *args, **kwargs
    ):
        keys = NewareCacheController.__keys(func, *args, **kwargs) # Expected Keys
        
        try:
            values = storage.json().mget(keys, '$')
            values = list(filter(None, values)) # Remove Empty entries
            values = list(chain(*values)) # Flat
            
            assert(len(values) == len(keys))
            
            df = concat(
                [NewareCacheController.__load(key, value) for key, value in zip(keys, values)],
                ignore_index=True
            )
            
            for column in df[NewareCacheController.PRIMARY_KEY].columns:
                df[column] = df[column].astype(int64)

            for column in df.filter(like='time').columns:
                df[column] = df[column].astype('datetime64[ms]')
            
            return df.convert_dtypes()

        except (AssertionError, redis.ResponseError):
            return DataFrame()
        
QUERY_TO_STORAGE_CONTROL = dict(
    neware_cache_query=NewareCacheController
)