#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos sntp fact class
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
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.sntp.sntp import SntpArgs
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.utils.utils import dict_has_key


class SntpFacts(object):
    """ The dmos sntp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = SntpArgs.argument_spec
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
        """ Populate the facts for sntp
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = connection.get(
                'show running-config sntp | details | nomore | display json')

        objs = []
        try:
            data_dict = json.loads(data)['data']
            data_list = data_dict['dmos-base:config']['dmos-sntp-interface:sntp']
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
            facts['sntp'] = params['config']

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
        config['auth'] = dict_has_key(conf, 'authenticate')

        auth_key_value = conf.get('authentication-key')
        if auth_key_value is not None:
            auth_key = []
            for each in auth_key_value:
                each_auth_key = dict()
                each_auth_key['id'] = each.get('id')
                each_auth_key['pass'] = each.get('md5')
                auth_key.append(each_auth_key)
            config['auth_key'] = auth_key

        config['client'] = dict_has_key(conf, 'client')

        config['max_poll'] = conf.get('max-poll')
        config['min_poll'] = conf.get('min-poll')

        source_value = conf.get('source')
        if source_value is not None:
            ipv4 = source_value.get('ipv4')
            if ipv4 is not None:
                config['source']['ipv4'] = ipv4['address']['ip']
            ipv6 = source_value.get('ipv6')
            if ipv6 is not None:
                config['source']['ipv6'] = ipv6['address']['ip']

        server_value = conf.get('server')
        if server_value is not None:
            server = []
            for each in server_value:
                each_server = dict()
                each_server['address'] = each.get('address')
                each_server['key_id'] = each.get('key')
                server.append(each_server)
            config['server'] = server

        return utils.remove_empties(config)
