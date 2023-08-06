import time
import mock
import sys
import socket
import zmq
import os
import unittest

import lumbermill.utils.DictUtils as DictUtils
from lumbermill.input import ZeroMQ
from tests.ModuleBaseTestCase import ModuleBaseTestCase
from tests.ServiceDiscovery import getFreeTcpPortoOnLocalhost

@unittest.skip("These tests sometimes seem to run into an endless loop. Need to look into this before reactivating.")
class TestZmq(ModuleBaseTestCase):

    def setUp(self):
        if 'TRAVIS' in os.environ and os.environ['TRAVIS'] == 'true':
            raise unittest.SkipTest('ZMQ module seems to be broken in travis docker container. Skipping test. <Assertion failed: pfd.revents & POLLIN (bundled/zeromq/src/signaler.cpp:239)>')
        super(TestZmq, self).setUp(ZeroMQ.ZeroMQ(mock.Mock()))

    def testZmqPull(self):
        ipaddr, port = getFreeTcpPortoOnLocalhost()
        self.test_object.configure({'address': '%s:%s' % (ipaddr, port),
                                    'pattern': 'pull'})
        self.checkConfiguration()
        self.test_object.start()
        message = 'A comfy chair is not an effective method of torture!'
        sender = self.getZmqSocket(ipaddr, port, 'push')
        self.assertTrue(sender is not None)
        for _ in range(0, 1000):
            sender.send(message)
        sender.close()
        expected_ret_val = DictUtils.getDefaultEventDict({'data': 'A comfy chair is not an effective method of torture!'})
        expected_ret_val.pop('lumbermill')
        event = False
        time.sleep(1)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertTrue(event is not False)
        event.pop('lumbermill')
        self.assertDictEqual(event, expected_ret_val)
        self.assertEqual(counter, 1000)

    def testZmqSubWithoutTopicFilter(self):
        ipaddr, port = self.getFreePortoOnLocalhost()
        self.test_object.configure({'address': '%s:%s' % (ipaddr, port),
                                    'pattern': 'sub'})
        self.checkConfiguration()
        self.test_object.start()
        message = 'Test A comfy chair is not an effective method of torture!'
        sender = self.getZmqSocket(ipaddr, port, 'pub')
        for _ in range(0, 100):
            sender.send(message)
        sender.close()
        expected_ret_val = DictUtils.getDefaultEventDict({'data': 'A comfy chair is not an effective method of torture!',
                                                      'topic': 'Test'})
        expected_ret_val.pop('lumbermill')
        event = False
        for event in self.receiver.getEvent():
            event.pop('lumbermill')
            self.assertDictEqual(event, expected_ret_val)
        self.assertTrue(event is not False)

    def testZmqSubWithTopicFilter(self):
        ipaddr, port = self.getFreePortoOnLocalhost()
        self.test_object.configure({'address': '%s:%s' % (ipaddr, port),
                                    'pattern': 'sub',
                                    'topic': 'Test'})
        self.checkConfiguration()
        self.test_object.start()
        message = 'Test A comfy chair is not an effective method of torture!'
        sender = self.getZmqSocket(ipaddr, port, 'pub')
        for _ in range(0, 100):
            sender.send(message)
        sender.close()
        expected_ret_val = DictUtils.getDefaultEventDict({'data': 'A comfy chair is not an effective method of torture!',
                                                      'topic': 'Test'})
        expected_ret_val.pop('lumbermill')
        self.assertTrue(self.receiver.hasEvents() is True)

    def testZmqSubWithFailingTopicFilter(self):
        ipaddr, port = self.getFreePortoOnLocalhost()
        self.test_object.configure({'address': '%s:%s' % (ipaddr, port),
                                    'pattern': 'sub',
                                    'topic': 'NotThere'})
        self.checkConfiguration()
        self.test_object.start()
        message = 'Test A comfy chair is not an effective method of torture!'
        sender = self.getZmqSocket(ipaddr, port, 'pub')
        for _ in range(0, 100):
            sender.send(message)
        sender.close()
        expected_ret_val = DictUtils.getDefaultEventDict({'data': 'A comfy chair is not an effective method of torture!',
                                                      'topic': 'Test'})
        expected_ret_val.pop('lumbermill')
        self.assertTrue(self.receiver.hasEvents() is False)

    def getZmqSocket(self, host, port, mode):
        context = zmq.Context()
        if mode == 'push':
            sock = context.socket(zmq.PUSH)
        else:
            sock = context.socket(zmq.PUB)
        try:
            sock.connect('tcp://%s:%s' % (host, port))
        except:
            etype, evalue, etb = sys.exc_info()
            print("Failed to connect to %s:%s. Exception: %s, Error: %s." % (host, port, etype, evalue))
            return None
        return sock
