#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos l3_interface fact class
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
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.l3_interface.l3_interface import L3_interfaceArgs


class L3_interfaceFacts(object):
    """ The dmos l3_interface fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = L3_interfaceArgs.argument_spec
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
        """ Populate the facts for l3_interface
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = connection.get(
                'show running-config interface l3 | details | nomore | display json')

        objs = []
        try:
            data_dict = json.loads(data)['data']
            data_list = data_dict['dmos-base:config']['interface']['dmos-ip-application:l3']
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
            facts['l3_interface'] = params['config']

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

        config['name'] = conf.get('name')
        config['description'] = conf.get('description')
        config['ip_mtu'] = conf.get('ip-mtu')
        config['vrf'] = conf.get('vrf')

        vlan_link_detect = conf.get('vlan-link-detect')
        if vlan_link_detect is not None:
            config['vlan_link_detect'] = vlan_link_detect.get('enabled')

        lower_layer_if = conf.get('lower-layer-if')
        if lower_layer_if is not None:
            config['lower_layer_if'] = lower_layer_if.get('vlan')

        ipv4 = conf.get('ipv4')
        if ipv4 is not None:
            address = ipv4.get('address')
            if address is not None:
                ipv4_dict = dict()
                ipv4_dict['address'] = address.get('ip')

                secondary = address.get('secondary')
                if secondary is not None:
                    secondary_list = []
                    for each in secondary:
                        secondary_list.append(each.get('ip'))

                    ipv4_dict['secondary'] = secondary_list

                config['ipv4'] = ipv4_dict

        ipv6 = conf.get('ipv6')
        if ipv6 is not None:
            ipv6_dict = dict()
            ipv6_dict['enable'] = ipv6.get('enable')

            address = ipv6.get('address')
            if address is not None:
                ipv6_list = []
                for each in address:
                    ipv6_list.append(each.get('ip'))

                ipv6_dict['address'] = ipv6_list

            nd = ipv6.get('nd')
            if nd is not None:
                ra = nd.get('ra')
                if ra is not None:
                    ra_dict = dict()
                    ra_dict['lifetime'] = ra.get('lifetime')
                    ra_dict['max_interval'] = ra.get('max-interval')
                    ra_dict['min_interval'] = ra.get('min-interval')
                    ra_dict['suppress'] = ra.get('suppress')

                    prefix = ra.get('prefix')
                    if prefix is not None:
                        prefix_list = []
                        for each in prefix:
                            prefix_dict = dict()
                            prefix_dict['ip'] = each.get('ip')
                            prefix_dict['no_advertise'] = each.get(
                                'no-advertise')
                            prefix_dict['no_autoconfig'] = each.get(
                                'no-autoconfig')
                            prefix_dict['off_link'] = each.get('off-link')

                            prefix_list.append(prefix_dict)
                        ra_dict['prefix'] = prefix_list

                    mtu = ra.get('mtu')
                    if mtu is not None:
                        ra_dict['mtu_suppress'] = mtu.get('suppress')

                    ipv6_dict['nd_ra'] = ra_dict

            config['ipv6'] = ipv6_dict

        return utils.remove_empties(config)
