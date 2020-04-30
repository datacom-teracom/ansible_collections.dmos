#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos lldp fact class
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
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.lldp.lldp import LldpArgs


class LldpFacts(object):
    """ The dmos lldp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = LldpArgs.argument_spec
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
        """ Populate the facts for lldp
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = connection.get(
                'show running-config lldp | details | nomore | display json')

        objs = []
        try:
            data_dict = json.loads(data)['data']
            data_list = data_dict['dmos-base:config']['dmos-lldp:lldp']
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
            facts['lldp'] = params['config']

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

        interface_value = conf.get('dmos-lldp-interface:interface')
        if interface_value is not None:
            interface = []
            for each in interface_value:
                each_interface = dict()
                each_interface['name'] = each.get('interface-name')
                each_interface['admin_status'] = each.get('admin-status')
                each_interface['notification'] = True if 'notification' in each else False

                tlvs = each.get('tlvs-tx')
                if tlvs is not None:
                    each_interface['tlv_port_description'] = tlvs.get('port-description')
                    each_interface['tlv_system_capabilities'] = tlvs.get('system-name')
                    each_interface['tlv_system_description'] = tlvs.get('system-description')
                    each_interface['tlv_system_name'] = tlvs.get('system-capabilities')

                interface.append(each_interface)
            config['interface'] = interface

        config['msg_fast_tx'] = conf.get('message-fast-tx')
        config['msg_tx_hold_multi'] = conf.get('message-tx-hold-multiplier')
        config['msg_tx_interval'] = conf.get('message-tx-interval')
        config['notification_interval'] = conf.get('notification-interval')
        config['reinit_delay'] = conf.get('reinit-delay')
        config['tx_credit_max'] = conf.get('tx-credit-max')
        config['tx_fast_init'] = conf.get('tx-fast-init')

        return utils.remove_empties(config)
