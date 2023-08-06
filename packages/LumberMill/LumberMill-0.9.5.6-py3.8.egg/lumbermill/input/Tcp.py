# -*- coding: utf-8 -*-
import sys
import ssl
import socket
import logging

from tornado import autoreload
from tornado.iostream import StreamClosedError
from tornado.netutil import bind_sockets
from tornado.tcpserver import TCPServer

import lumbermill.utils.DictUtils as DictUtils
from lumbermill.BaseModule import BaseModule
from lumbermill.utils.Decorators import ModuleDocstringParser


class TornadoTcpServer(TCPServer):

    def __init__(self, io_loop=None, ssl_options=None, gp_module=False, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.gp_module = gp_module
        try:
            TCPServer.__init__(self, ssl_options=ssl_options, **kwargs)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not create tcp server. Exception: %s, Error: %s." % (etype, evalue))
            self.gp_module.shutDown()

    def handle_stream(self, stream, address):
        ConnectionHandler(stream, address, self.gp_module)

class ConnectionHandler(object):

    def __init__(self, stream, address, gp_module):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.gp_module = gp_module
        self.simple_separator = self.gp_module.getConfigurationValue('simple_separator')
        self.regex_separator = self.gp_module.getConfigurationValue('regex_separator')
        self.chunksize = self.gp_module.getConfigurationValue('chunksize')
        self.mode = self.gp_module.getConfigurationValue('mode')
        self.encoding = self.gp_module.getConfigurationValue('encoding')
        self.is_open = True
        self.stream = stream
        self.address = address
        self.host, self.port = self.address[0], self.address[1]
        self.stream.set_close_callback(self._on_close)
        try:
            if not self.stream.closed():
                if self.mode == 'line' and self.regex_separator:
                    self.stream.read_until_regex(bytes(self.regex_separator, "utf-8"), self._on_read_line)
                elif self.mode == 'line':
                    self.stream.read_until(bytes(self.simple_separator, "utf-8"), self._on_read_line)
                else:
                    self.stream.read_bytes(self.chunksize, self._on_read_chunk)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not read from socket %s. Exception: %s, Error: %s." % (self.address, etype, evalue))

    def _on_read_line(self, data):
        data = data.strip()
        if data == "":
            return
        self.sendEvent(data)
        try:
            if not self.stream.reading():
                if self.regex_separator:
                    self.stream.read_until_regex(bytes(self.regex_separator, "utf-8"), self._on_read_line)
                else:
                    self.stream.read_until(bytes(self.simple_separator, "utf-8"), self._on_read_line)
        except StreamClosedError:
            pass
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not read from socket %s. Exception: %s, Error: %s." % (self.address, etype, evalue))

    def _on_read_chunk(self, data):
        data = data.strip()
        if data == "":
            return
        self.sendEvent(data)
        try:
            if not self.stream.reading():
                self.stream.read_bytes(self.chunksize, self._on_read_chunk)
        except StreamClosedError:
            pass
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Failed to read from socket %s. Exception: %s, Error: %s." % (self.address, etype, evalue))

    def _on_close(self):
        # Send remaining buffer if neccessary.
        data = ""
        if self.mode == 'stream' and self.stream._read_buffer_size > 0:
            while True:
                try:
                    data += self.stream._read_buffer.popleft().strip()
                except IndexError:
                    break
                except AttributeError:
                    #print(self.stream._read_buffer)
                    sys.exit()
        if data != "":
            self.sendEvent(data)
        self.stream.close()

    def sendEvent(self, data):
        self.gp_module.sendEvent(DictUtils.getDefaultEventDict({"data": data}, caller_class_name="TcpServer", received_from="%s:%d" % (self.host, self.port)))

@ModuleDocstringParser
class Tcp(BaseModule):
    r"""
    Reads data from tcp socket and sends it to its outputs.
    Should be the best choice perfomancewise if you are on Linux and are running with multiple workers.

    interface:  Ipaddress to listen on.
    port:       Port to listen on.
    timeout:    Sockettimeout in seconds.
    tls:        Use tls or not.
    key:        Path to tls key file.
    cert:       Path to tls cert file.
    cacert:     Path to ca cert file.
    tls_proto:  Set TLS protocol version.
    mode:       Receive mode, line or stream.
    simple_separator:  If mode is line, set separator between lines.
    regex_separator:   If mode is line, set separator between lines. Here regex can be used. The result includes the data that matches the regex.
    chunksize:  If mode is stream, set chunksize in bytes to read from stream.
    max_buffer_size: Max kilobytes to in receiving buffer.
    encoding:   Encoding of the input data.

    Configuration template:

    - input.TcpServer:
       interface:                       # <default: ''; type: string; is: optional>
       port:                            # <default: 5151; type: integer; is: optional>
       timeout:                         # <default: None; type: None||integer; is: optional>
       tls:                             # <default: False; type: boolean; is: optional>
       key:                             # <default: False; type: boolean||string; is: required if tls is True else optional>
       cert:                            # <default: False; type: boolean||string; is: required if tls is True else optional>
       cacert:                          # <default: False; type: boolean||string; is: optional>
       tls_proto:                       # <default: 'TLSv1'; type: string; values: ['TLSv1', 'TLSv1_1', 'TLSv1_2']; is: optional>
       mode:                            # <default: 'line'; type: string; values: ['line', 'stream']; is: optional>
       simple_separator:                # <default: '\n'; type: string; is: optional>
       regex_separator:                 # <default: None; type: None||string; is: optional>
       chunksize:                       # <default: 16384; type: integer; is: required if mode == 'stream' else optional>
       max_buffer_size:                 # <default: 10240; type: integer; is: optional>
       encoding:                        # <default: 'utf-8'; type: string; is: optional>
       receivers:
        - NextModule
    """

    module_type = "input"
    """Set module type"""
    can_run_forked = True

    def configure(self, configuration):
        # Call parent configure method
        BaseModule.configure(self, configuration)
        self.server = False
        self.max_buffer_size = self.getConfigurationValue('max_buffer_size') * 10240 #* 10240
        self.start_ioloop = False
        try:
            self.sockets = bind_sockets(self.getConfigurationValue("port"), self.getConfigurationValue("interface"), backlog=128)
            for server_socket in self.sockets:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not listen on %s:%s. Exception: %s, Error: %s." % (self.getConfigurationValue("interface"),
                                                                                        self.getConfigurationValue("port"), etype, evalue))
            self.lumbermill.shutDown()
            return
        autoreload.add_reload_hook(self.shutDown)

    def getStartMessage(self):
        start_msg = "listening on %s:%s" % (self.getConfigurationValue("interface"), self.getConfigurationValue("port"))
        if self.getConfigurationValue("tls"):
            start_msg += " (with %s)" % self.getConfigurationValue("tls_proto")
        return start_msg

    def initAfterFork(self):
        BaseModule.initAfterFork(self)
        ssl_options = None
        if self.getConfigurationValue("tls"):
            ssl_options = {'ssl_version': getattr(ssl, "PROTOCOL_%s" % self.getConfigurationValue("tls_proto")),
                           'certfile': self.getConfigurationValue("cert"),
                           'keyfile': self.getConfigurationValue("key")}
        self.server = TornadoTcpServer(ssl_options=ssl_options, gp_module=self, max_buffer_size=self.max_buffer_size)
        self.server.add_sockets(self.sockets)

    def shutDown(self):
        if not self.is_configured:
            return
        if self.server:
            self.server.stop()
        for server_socket in self.sockets:
            try:
                server_socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            server_socket.close()
