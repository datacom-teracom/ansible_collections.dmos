#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos user fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from copy import deepcopy
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.user.user import UserArgs
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.utils.utils import dict_has_key
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.utils.utils import parse_current_config


class UserFacts(object):
    """ The dmos user fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = UserArgs.argument_spec
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
        """ Populate the facts for user
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if connection:  # just for linting purposes, remove
            pass

        # split the config into instances of the resource
        if not data:
            data = connection.get(
                'show running-config user | details | nomore | display keypath'
            )

        config = parse_current_config(data, self.argument_spec, 'user', {
                                      'user': 'name', 'alias': 'name'})

        facts = {}
        if config:
            params = utils.validate_config(self.argument_spec, config)
            facts['user'] = params['config']

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
        pass
