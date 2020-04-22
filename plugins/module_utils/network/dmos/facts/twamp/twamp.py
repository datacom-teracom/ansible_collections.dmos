#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos twamp fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.twamp.twamp import TwampArgs


class TwampFacts(object):
    """ The dmos twamp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = TwampArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for twamp
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = connection.get(
                'show running-config oam twamp | details | nomore | display json')

        objs = []
        try:
            data_dict = json.loads(data)['data']
            data_list = data_dict['dmos-base:config']['oam']['dmos-twamp-app:twamp']
        except (ValueError, KeyError):
            pass
        else:
            data_list = data_list if isinstance(data_list, list) else [data_list]
            for each in data_list:
                obj = self.render_config(self.generated_spec, each)
                if obj:
                    objs.append(obj)

        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['twamp'] = params['config']

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        reflector = conf.get('reflector')
        if reflector is not None:
            reflector_dict = {}

            reflector_dict['admin_status'] = reflector.get('administrative-status')
            reflector_dict['port'] = reflector.get('port')

            ipv4 = reflector.get('ipv4')
            if ipv4 is not None:
                ipv4_dict = {}

                client_address = ipv4.get('client-address')
                if client_address:
                    client_address_list = []
                    for each in client_address:
                        each_client_address = {}
                        each_client_address['address'] = each.get('ip')
                        each_client_address['state'] = each.get('state')

                        client_address_list.append(each_client_address)

                    ipv4_dict['client_address'] = client_address_list

                client_network = ipv4.get('client-network')
                if client_network:
                    client_network_list = []
                    for each in client_network:
                        each_client_network = {}
                        each_client_network['network'] = each.get('ip')
                        each_client_network['state'] = each.get('state')

                        client_network_list.append(each_client_network)

                    ipv4_dict['client_network'] = client_network_list

                reflector_dict['ipv4'] = ipv4_dict

            ipv6 = reflector.get('ipv6')
            if ipv6 is not None:
                ipv6_dict = {}

                client_address = ipv6.get('client-address')
                if client_address:
                    client_address_list = []
                    for each in client_address:
                        each_client_address = {}
                        each_client_address['address'] = each.get('ip')
                        each_client_address['state'] = each.get('state')

                        client_address_list.append(each_client_address)

                    ipv6_dict['client_address'] = client_address_list

                client_network = ipv6.get('client-network')
                if client_network:
                    client_network_list = []
                    for each in client_network:
                        each_client_network = {}
                        each_client_network['network'] = each.get('ip')
                        each_client_network['state'] = each.get('state')

                        client_network_list.append(each_client_network)

                    ipv6_dict['client_network'] = client_network_list

                reflector_dict['ipv6'] = ipv6_dict

            config['reflector'] = reflector_dict

        sender = conf.get('dmos-twamp-app-client:sender')
        if sender is not None:
            sender_dict = {}

            sender_dict['admin_status'] = sender.get('administrative-status')

            connection = sender.get('connection')
            if connection:
                connection_list = []
                for each in connection:
                    each_connection = {}

                    each_connection['id'] = each.get('id')
                    each_connection['admin_status'] = each.get('administrative-status')

                    ipv4 = each.get('ipv4')
                    if ipv4 is not None:
                        ipv4_dict = {}

                        source_address = ipv4.get('source-address')
                        if source_address:
                            ipv4_dict['source_address'] = source_address[0]['ip']

                        target_address = ipv4.get('target-address')
                        if target_address:
                            ipv4_dict['target_address'] = target_address[0]['ip']

                        each_connection['ipv4'] = ipv4_dict

                    ipv6 = each.get('ipv6')
                    if ipv6 is not None:
                        ipv6_dict = {}

                        source_address = ipv6.get('source-address')
                        if source_address:
                            ipv6_dict['source_address'] = source_address[0]['ip']

                        target_address = ipv6.get('target-address')
                        if target_address:
                            ipv6_dict['target_address'] = target_address[0]['ip']

                        each_connection['ipv6'] = ipv6_dict

                    each_connection['number_of_packets'] = each.get(
                        'number-of-packets')
                    each_connection['server_port'] = each.get('server-port')
                    each_connection['test_interval'] = each.get('test-interval')

                    test_session = each.get('test-session')
                    if test_session:
                        test_session_list = []
                        for each_test_session in test_session:
                            each_test_session_dict = {}

                            each_test_session_dict['id'] = each_test_session.get('id')

                            ipv4 = each_test_session.get('ipv4')
                            if ipv4 is not None:
                                ipv4_dict = {}

                                source_address = ipv4.get('source-address')
                                if source_address:
                                    ipv4_dict['source_address'] = source_address[0]['ip']

                                target_address = ipv4.get('target-address')
                                if target_address:
                                    ipv4_dict['target_address'] = target_address[0]['ip']

                                each_test_session_dict['ipv4'] = ipv4_dict

                            ipv6 = each_test_session.get('ipv6')
                            if ipv6 is not None:
                                ipv6_dict = {}

                                source_address = ipv6.get('source-address')
                                if source_address:
                                    ipv6_dict['source_address'] = source_address[0]['ip']

                                target_address = ipv6.get('target-address')
                                if target_address:
                                    ipv6_dict['target_address'] = target_address[0]['ip']

                                each_test_session_dict['ipv6'] = ipv6_dict

                            each_test_session_dict['max_port'] = each_test_session.get('max-port')
                            each_test_session_dict['min_port'] = each_test_session.get('min-port')
                            each_test_session_dict['dscp'] = each_test_session.get('dscp')
                            each_test_session_dict['packet_size'] = each_test_session.get(
                                'packet-size')

                            test_session_list.append(each_test_session_dict)

                        each_connection['test_session'] = test_session_list

                    connection_list.append(each_connection)

                sender_dict['connection'] = connection_list

            config['sender'] = sender_dict

        return utils.remove_empties(config)
