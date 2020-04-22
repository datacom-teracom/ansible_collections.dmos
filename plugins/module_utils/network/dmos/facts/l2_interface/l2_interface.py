#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos l2_interface fact class
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
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.l2_interface.l2_interface import L2_interfaceArgs
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.utils.utils import dict_has_key


class L2_interfaceFacts(object):
    """ The dmos l2_interface fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = L2_interfaceArgs.argument_spec
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
        """ Populate the facts for l2_interface
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = connection.get(
                'show running-config switchport | details | nomore | display json')

        objs = []
        try:
            data_dict = json.loads(data)['data']
            data_list = data_dict['dmos-base:config']['switchport-native-vlan:switchport']['interface']
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
            params = utils.validate_config(
                self.argument_spec, {'config': objs})
            facts['l2_interface'] = params['config']

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
        config['interface_name'] = conf.get('interface-name')

        native_vlan = conf.get('native-vlan')
        if native_vlan is not None:
            config['native_vlan_id'] = native_vlan.get('vlan-id')

        config['qinq'] = dict_has_key(conf, 'switchport-qinq:qinq')

        storm_control = conf.get('dmos-storm-control:storm-control')
        if storm_control is not None:
            storm_control_list = []

            broadcast = storm_control.get('broadcast')
            if broadcast is not None:
                percent = broadcast.get('percent')
                if percent is not None:
                    storm_control_list.append(
                        {'traffic': 'broadcast', 'percent': percent})

            multicast = storm_control.get('multicast')
            if multicast is not None:
                percent = multicast.get('percent')
                if percent is not None:
                    storm_control_list.append(
                        {'traffic': 'multicast', 'percent': percent})

            unicast = storm_control.get('unicast')
            if unicast is not None:
                percent = unicast.get('percent')
                if percent is not None:
                    storm_control_list.append(
                        {'traffic': 'unicast', 'percent': percent})

            config['storm_control'] = storm_control_list

        config['tpid'] = conf.get('switchport-tpid:tpid')

        return utils.remove_empties(config)
