# -*- coding: utf-8 -*-
import sys
import redis
from pickle import dumps, loads

from lumbermill.BaseThreadedModule import BaseThreadedModule
from lumbermill.utils.Buffers import Buffer
from lumbermill.utils.Decorators import ModuleDocstringParser


@ModuleDocstringParser
class Cache(BaseThreadedModule):
    """
    A simple wrapper around the python simplekv module.

    It can be used to store results of modules in all simplekv supported backends.

    When set, the following options cause RedisStore to use a buffer for setting values.
    Multiple values are set via the pipe command, which speeds up storage. Still this comes at a price.
    Buffered values, that have not yet been send to redis, will be lost when LumberMill crashes.

    backend: backends supported by [simplekv](http://pythonhosted.org//simplekv/)
    store_interval_in_secs: Sending data to redis in x seconds intervals.
    batch_size: Sending data to redis if count is above, even if store_interval_in_secs is not reached.
    backlog_size: Maximum count of values waiting for transmission. Values above count will be dropped.

    Configuration template:

    - Cache:
       backend:                         # <default: 'DictStore'; type: string; values:['DictStore', 'RedisStore', 'MemcacheStore']; is: optional>
       server:                          # <default: None; type: None||string; is: required if backend in ['RedisStore', 'MemcacheStore'] and cluster is None else optional>
       cluster:                         # <default: None; type: None||dictionary; is: required if backend == 'RedisStore' and server is None else optional>
       port:                            # <default: 6379; type: integer; is: optional>
       db:                              # <default: 0; type: integer; is: optional>
       password:                        # <default: None; type: None||string; is: optional>
       socket_timeout:                  # <default: 10; type: integer; is: optional>
       charset:                         # <default: 'utf-8'; type: string; is: optional>
       errors:                          # <default: 'strict'; type: string; is: optional>
       decode_responses:                # <default: False; type: boolean; is: optional>
       unix_socket_path:                # <default: None; type: None||string; is: optional>
       batch_size:                      # <default: None; type: None||integer; is: optional>
       store_interval_in_secs:          # <default: None; type: None||integer; is: optional>
       backlog_size:                    # <default: 5000; type: integer; is: optional>
    """
    module_type = "stand_alone"
    """Set module type"""

    def configure(self, configuration):
        # Call parent configure method
        BaseThreadedModule.configure(self, configuration)
        self.backend = self.getConfigurationValue('backend')
        self.backend_client = None
        self.kv_store = None
        self.set_buffer = None
        if self.backend == 'DictStore':
            import simplekv.memory
            self.kv_store = simplekv.memory.DictStore()
        elif self.backend == 'RedisStore':
            import simplekv.memory.redisstore
            self.backend_client = self._getRedisClient()
            self.kv_store = simplekv.memory.redisstore.RedisStore(self.backend_client)
        elif self.backend == 'MemcacheStore':
            import simplekv.memory.memcachestore
            self.backend_client = self._getMemcacheClient()
            self.kv_store = simplekv.memory.memcachestore.MemcacheStore(self.backend_client)
        else:
            self.logger("Unknown backend type %s. Please check." % backend)
            self.lumbermill.shutDown();

        if self.getConfigurationValue('store_interval_in_secs') or self.getConfigurationValue('batch_size'):
            if self.backend == 'RedisStore':
                self.set_buffer = Buffer(self.getConfigurationValue('batch_size'), self._setRedisBufferedCallback, self.getConfigurationValue('store_interval_in_secs'), maxsize=self.getConfigurationValue('backlog_size'))
            else:
                self.set_buffer = Buffer(self.getConfigurationValue('batch_size'), self._setBufferedCallback, self.getConfigurationValue('store_interval_in_secs'), maxsize=self.getConfigurationValue('backlog_size'))
            self._set = self.set
            self.set = self._setBuffered
            self._get = self.get
            self.get = self._getBuffered
            self._delete = self.delete
            self.delete = self._deleteBuffered
            self._pop = self.pop
            self.pop = self._popBuffered

    def _getRedisClient(self):
        if not self.getConfigurationValue('cluster') or len(self.getConfigurationValue('cluster')) == 0:
            redis_store = self.getConfigurationValue('server')
            client = self._getSimpleRedisClient()
        else:
            redis_store = self.getConfigurationValue('cluster')
            client = self._getClusterRedisClient()
        try:
            client.ping()
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not connect to redis store at %s. Exception: %s, Error: %s." % (redis_store, etype, evalue))
            self.lumbermill.shutDown()
        return client

    def _getMemcacheClient(self):
        client = None
        # TODO: implement memcache client
        return client

    def _getSimpleRedisClient(self):
        try:
            client = redis.StrictRedis(host=self.getConfigurationValue('server'),
                                       port=self.getConfigurationValue('port'),
                                       db=self.getConfigurationValue('db'),
                                       password=self.getConfigurationValue('password'),
                                       socket_timeout=self.getConfigurationValue('socket_timeout'),
                                       charset=self.getConfigurationValue('charset'),
                                       errors=self.getConfigurationValue('errors'),
                                       decode_responses=self.getConfigurationValue('decode_responses'),
                                       unix_socket_path=self.getConfigurationValue('unix_socket_path'))
            return client
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not connect to redis store at %s. Exception: %s, Error: %s." % (self.getConfigurationValue['server'], etype, evalue))
            self.lumbermill.shutDown()

    def _getClusterRedisClient(self):
        try:
            import rediscluster
        except ImportError:
            self.logger.error("Could not import rediscluster module. To install follow instructions @https://github.com/salimane/rediscluster-py")
            self.lumbermill.shutDown()
        # TODO: Implement a locking mechanism for the cluster client.
        # Some modules like Facet depend on this.
        cluster = {'nodes': {}, 'master_of': {}}
        counter = 1
        for master_node, slave_nodes in self.getConfigurationValue('cluster').items():
            master_node_key = "node_%d" % counter
            node_name_or_ip, node_port = self._parseRedisServerAddress(master_node)
            cluster['nodes'].update({master_node_key: {'host': node_name_or_ip, 'port': node_port}})
            if 'default_node' not in cluster:
                cluster['default_node'] = master_node
            if type(slave_nodes) is str:
                slave_nodes = [slave_nodes]
            for slave_node in slave_nodes:
                counter += 1
                slave_node_key = "node_%d" % counter
                node_name_or_ip, node_port = self._parseRedisServerAddress(slave_node)
                cluster['nodes'].update({slave_node_key: {'host':node_name_or_ip, 'port': node_port}})
                cluster['master_of'].update({master_node_key: slave_node_key})
        try:
            client = rediscluster.StrictRedisCluster(cluster=cluster, db=self.getConfigurationValue('db'))
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not connect to redis store at %s. Exception: %s, Error: %s." % (self.getConfigurationValue['cluster'], etype, evalue))
            self.lumbermill.shutDown()
        return client

    def _parseRedisServerAddress(self, node_address):
        try:
            node_name_or_ip, node_port = node_address.split(":")
        except ValueError:
            node_name_or_ip = node_address
            node_port = self.getConfigurationValue('port')
        return (node_name_or_ip, node_port)

    def getBackendName(self):
        return self.backend

    def iterKeys(self):
        for key in self.kv_store.iter_keys():
            yield key

    def getClient(self):
        return self.backend_client

    def getLock(self, name, timeout=None, sleep=0.1):
        lock = False
        try:
            lock = self.backend_client.lock(name, timeout, sleep)
        except AttributeError:
            pass
        return lock

    def set(self, key, value, ttl=0, pickle=True):
        if pickle is True:
            try:
                value = dumps(value)
            except:
                etype, evalue, etb = sys.exc_info()
                self.logger.error("Could not store %s:%s in redis. Exception: %s, Error: %s." % (key, value, etype, evalue))
                raise
        # Only backend clients support ttl.
        if self.backend_client and ttl:
            self.kv_store.put(key, value, ttl_secs=ttl)
        else:
            self.kv_store.put(key, value)

    def _setBuffered(self, key, value, ttl=0, pickle=True):
        self.set_buffer.append({'key': key, 'value': value, 'ttl': ttl, 'pickle': pickle})

    def _setBufferedCallback(self, values):
        for value in values:
            self._set(value['key'], value['value'], value['ttl'], value['pickle'])

    def _setRedisBufferedCallback(self, values):
        pipe = self.backend_client.pipeline()
        for value in values:
            if value['pickle'] is True:
                try:
                    value['value'] = dumps(value['value'])
                except:
                    etype, evalue, etb = sys.exc_info()
                    self.logger.error("Could not store %s:%s in redis. Exception: %s, Error: %s." % (value['key'], value['value'], etype, evalue))
                    raise
            if(value['ttl'] == 0):
                pipe.set(value['key'], value['value'])
            else:
                pipe.setex(value['key'], value['ttl'], value['value'])
        try:
            pipe.execute()
            return True
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not flush buffer. Exception: %s, Error: %s." % (etype, evalue))

    def get(self, key, unpickle=True):
        value = self.kv_store.get(key)
        if unpickle and value:
            try:
                value = loads(value)
            except:
                etype, evalue, etb = sys.exc_info()
                self.logger.error("Could not unpickle %s:%s from redis. Exception: %s, Error: %s." % (key, value, etype, evalue))
                raise
        return value

    def _getBuffered(self, key, unpickle=True):
        try:
            value_idx = next(index for (index, entry) in enumerate(self.set_buffer.buffer) if entry["key"] == key)
            return self.set_buffer.buffer[value_idx]['value']
        except:
            return self._get(key, unpickle)

    def delete(self, key):
        self.kv_store.delete(key)

    def _deleteBuffered(self, key):
        try:
            value_idx = next(index for (index, entry) in enumerate(self.set_buffer.buffer) if entry["key"] == key)
            self.set_buffer.buffer.pop(value_idx)
            return
        except:
            self._delete(key)

    def pop(self, key, unpickle=True):
        value = self.get(key, unpickle)
        if value:
            self.delete(key)
        return value

    def _popBuffered(self, key, unpickle=True):
        try:
            value_idx = next(index for (index, entry) in enumerate(self.set_buffer.buffer) if entry["key"] == key)
            return self.set_buffer.buffer.pop(value_idx)['value']
        except:
            return self._pop(key, unpickle)

    def shutDown(self):
        try:
            self.buffer.flush()
        except:
            pass
        BaseThreadedModule.shutDown(self)
