#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos log fact class
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
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.log.log import LogArgs


class LogFacts(object):
    """ The dmos log fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = LogArgs.argument_spec
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
        """ Populate the facts for log
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = connection.get(
                'show running-config log | details | nomore | display json')

        objs = []
        try:
            data_dict = json.loads(data)['data']
            data_list = data_dict['dmos-base:config']['dmos-log-manager:log']
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
            facts['log'] = params['config']

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
        config['severity'] = conf.get('severity')

        syslog_value = conf.get('syslog')
        if syslog_value is not None:
            syslog = []
            for each in syslog_value['host']:
                syslog.append(each['address'])
            config['syslog'] = syslog

        return utils.remove_empties(config)
