# -*- coding: utf-8 -*-
import os
import sys
import abc
import logging
from functools import wraps

from lumbermill.constants import LOGLEVEL_STRING_TO_LOGLEVEL_INT
from lumbermill.utils.ConfigurationValidator import ConfigurationValidator
from lumbermill.utils.DynamicValues import parseDynamicValue, mapDynamicValue


class BaseModule:
    """
    Base class for all lumbermill modules.

    If you happen to override one of the methods defined here, be sure to know what you
    are doing. You have been warned ;)

    Configuration template:

    - module: SomeModuleName
       id:                               # <default: ""; type: string; is: optional>
       filter:                           # <default: None; type: None||string; is: optional>
       add_fields:                       # <default: {}; type: dict; is: optional>
       delete_fields:                    # <default: []; type: list; is: optional>
       event_type:                       # <default: None; type: None||string; is: optional>
       set_internal:                     # <default: {}; type: dict; is: optional>
       log_level:                        # <default: 'info'; type: string; values: ['info', 'warn', 'error', 'critical', 'fatal', 'debug']; is: optional>
       ...
       receivers:
        - ModuleName
        - ModuleAlias
    """

    module_type = "generic"
    """ Set module type. """
    can_run_forked = True

    def __init__(self, lumbermill):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.lumbermill = lumbermill
        self.receivers = {}
        self.configuration_data = {}
        self.input_filter = None
        self.output_filters = {}
        self.process_id = os.getpid()
        self.is_configured = False

    def configure(self, configuration=None):
        """
        Configure the module.
        This method will be called by the LumberMill main class after initializing the module
        and after the configure method of the module is called.
        The configuration parameter contains k:v pairs of the yaml configuration for this module.

        @param configuration: dictionary
        @return: void
        """
        if configuration:
            self.configuration_data.update(configuration)
        self.parseDynamicValuesInConfiguration()
        # Set log level.
        self.logger.setLevel(LOGLEVEL_STRING_TO_LOGLEVEL_INT[self.getConfigurationValue('log_level').lower()])
        # Set default actions.
        self.delete_fields = self.getConfigurationValue('delete_fields')
        self.add_fields = self.getConfigurationValue('add_fields')
        self.event_type = self.getConfigurationValue('event_type')
        self.set_internal = self.getConfigurationValue('set_internal')
        # Set input filter.
        if self.getConfigurationValue('filter'):
            self.setInputFilter(self.getConfigurationValue('filter'))
        # Set output filter per receiver if configured.
        if 'receivers' in self.configuration_data:
            for receiver_config in self.getConfigurationValue('receivers'):
                if not isinstance(receiver_config, dict):
                    continue
                receiver_name, receiver_filter_config = next(iter(receiver_config.items()))
                self.addOutputFilter(receiver_name, receiver_filter_config['filter'])
        self.checkConfiguration()
        self.is_configured = True

    def parseDynamicValuesInConfiguration(self):
        """
        Replace the configuration notation for dynamic values with pythons notation.
        E.g:
        id: myid_$(event.lumbermill.event_id)
        parsed:
        id: %(event.lumbermill.event_id)s == 'TcpServer'
        """
        # Copy dict since we might change it during iteration.
        configuration_data_copy = self.configuration_data.copy()
        for key, value in configuration_data_copy.items():
            self.configuration_data[key] = parseDynamicValue(key, value)

    def checkConfiguration(self):
        configuration_errors = ConfigurationValidator().validateModuleConfiguration(self)
        if configuration_errors:
            self.logger.error("Could not configure module %s. Problems: %s." % (self.__class__.__name__, configuration_errors))
            self.lumbermill.shutDown()

    def getLumberMillInstance(self):
        return self.lumbermill

    def getStartMessage(self):
        """
        Return a start message for the module. Can be overwritten to customize the message, e.g. to include port a server is
        listening on.
        """
        return 'started'

    def isDynamicConfigurationValue(self, key):
        config_setting = None
        try:
            config_setting = self.configuration_data[key]
        except KeyError:
            self.logger.warning("Could not find configuration setting for: %s." % key)
            self.lumbermill.shutDown()
        if not isinstance(config_setting, dict):
            self.logger.debug("Configuration for key: %s is incorrect." % key)
            return False
        return config_setting['contains_dynamic_value']

    def getConfigurationValue(self, key, mapping_dict={}, use_strftime=False):
        """
        Get a configuration value. This method encapsulates the internal configuration dictionary and
        takes care of replacing dynamic variables of the pattern e.g. $(field_name) with the corresponding
        entries of the mapping dictionary. Most of the time, this will be the data dictionary.

        It will also take care to return a default value if the module doc string provided one.
        """
        # Test if requested key exists.
        #config_setting = self.configuration_data[key]
        config_setting = None
        try:
            config_setting = self.configuration_data[key]
        except KeyError:
            self.logger.warning("Could not find configuration setting for: %s." % key)
            self.lumbermill.shutDown()
        if not isinstance(config_setting, dict):
            self.logger.debug("Configuration for key: %s is incorrect." % key)
            return False
        if config_setting['contains_dynamic_value'] is False or not mapping_dict:
            return config_setting.get('value')
        return mapDynamicValue(config_setting.get('value'), mapping_dict, use_strftime)

    def addReceiver(self, receiver_name, receiver):
        if self.module_type != "output":
            self.receivers[receiver_name] = receiver

    def setInputFilter(self, filter_string):
        """
        Convert input filter to lamba function.
        E.g. original filter:
        filter: $(lumbermill.source_module) == 'TcpServer'
        converts to:
        lambda event : event.get('lumbermill.source_module', False) == 'TcpServer'
        """
        try:
            event_filter = eval(filter_string)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Failed to compile filter: %s. Exception: %s, Error: %s." % (filter_string, etype, evalue))
            self.lumbermill.shutDown()
        # Wrap default receiveEvent method with filtered one.
        self.wrapReceiveEventWithFilter(event_filter, filter_string)

    def addOutputFilter(self, receiver_name, filter_string):
        """
        Convert output filter to lamba function.
        E.g. original filter:
        filter: $(lumbermill.source_module) == 'TcpServer'
        converts to:
        lambda event : event.get('lumbermill.source_module', False) == 'TcpServer'
        """
        try:
            output_filter = eval(filter_string)
            self.output_filters[receiver_name] = output_filter
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Failed to compile filter: %s. Exception: %s, Error: %s." % (filter_string, etype, evalue))
            self.lumbermill.shutDown()

    def getFilteredReceivers(self, event):
        if not self.output_filters:
            return self.receivers
        filterd_receivers = {}
        for receiver_name, receiver in self.receivers.items():
            if receiver_name not in self.output_filters:
                filterd_receivers[receiver_name] = receiver
                continue
            try:
                # The filter needs the event variable to work correctly.
                matched = self.output_filters[receiver_name](self.lumbermill, event)
            except:
                etype, evalue, etb = sys.exc_info()
                self.logger.warning("Output filter for %s failed. Exception: %s, Error: %s." % (receiver_name, etype, evalue))
                print(event)
                continue
            # If the filter succeeds, the data will be send to the receiver.
            if matched:
                filterd_receivers[receiver_name] = receiver
        return filterd_receivers

    def initAfterFork(self):
        """
        Call startInterval on receiver buffered queue.
        This is done here since the buffer uses a thread to flush buffer in
        given intervals. The thread will not survive a fork of the main process.
        So we need to start this after the fork was executed.
        """
        self.process_id = os.getpid()
        for receiver_name, receiver in self.receivers.items():
            if isinstance(receiver, BaseModule) and hasattr(receiver, 'put'):
                receiver.startInterval()

    def commonActions(self, event):
        #if not self.input_filter or self.input_filter_matched:
        # Add fields if configured.
        if self.add_fields:
            for field_name, field_value in mapDynamicValue(self.add_fields, event).items():
                try:
                    event[field_name] = field_value
                except KeyError:
                    self.logger.warning("KeyError: could not set %s: %s" % (field_name, field_value))
        # Delete fields if configured.
        for field_name in self.delete_fields:
            try:
                event.pop(field_name, None)
            except (KeyError, AttributeError) as e:
                self.logger.warning("KeyError: could not delete %s." % field_name)
        if self.event_type:
            event['lumbermill']['event_type'] = mapDynamicValue(self.event_type, event)
        if self.set_internal:
            self.lumbermill.setInInternalDataStore(self.set_internal['key'], mapDynamicValue(self.set_internal['value'], event))
        return event

    def sendEvent(self, event, apply_common_actions=True):
        receivers = self.receivers if not self.output_filters else self.getFilteredReceivers(event)
        if not receivers:
            return
        if(apply_common_actions):
            event = self.commonActions(event)
        if len(receivers) > 1:
            event_clone = event.copy()
        copy_event = False
        for receiver in receivers.values():
            self.logger.debug("Sending event from %s to %s" % (self, receiver))
            if hasattr(receiver, 'receiveEvent'):
                receiver.receiveEvent(event if not copy_event else event_clone.copy())
            else:
                receiver.put(event if not copy_event else event_clone.copy())
            copy_event = True

    def receiveEvent(self, event):
        for event in self.handleEvent(event):
            if event:
                self.sendEvent(event)

    def wrapReceiveEventWithFilter(self, event_filter, filter_string):
        wrapped_func = self.receiveEvent
        @wraps(wrapped_func)
        def receiveEventFiltered(event):
            try:
                if event_filter(self.lumbermill, event):
                    wrapped_func(event)
                else:
                    # Common actions will only be applied if the filter for the module matched.
                    self.sendEvent(event, apply_common_actions=False)
            except:
                etype, evalue, etb = sys.exc_info()
                self.logger.warning("Filter <%s> failed. Exception: %s, Error: %s." % (filter_string, etype, evalue))
                # Pass event to next module.
                # Common actions will only be applied if the filter for the module matched.
                self.sendEvent(event, apply_common_actions=False)
        self.receiveEvent = receiveEventFiltered

    @abc.abstractmethod
    def handleEvent(self, event):
        """
        Process the event.

        @param event: dictionary
        """
        yield event

    def shutDown(self):
        self.alive = False
