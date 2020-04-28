#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for dmos_facts
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': [u'preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: dmos_facts
version_added: '2.9'
short_description: Get facts about dmos devices.
description:
  - Collects facts from network devices running the dmos operating
    system. This module places the facts gathered in the fact tree keyed by the
    respective resource name.  The facts module will always collect a
    base set of facts from the device and can enable or disable
    collection of additional facts.
author:
    - Vinicius Kleinubing (@vgkleinubing) <vinicius.grubel@datacom.com.br>
    - LDS Labs (@lds-labs)
options:
  gather_subset:
    description:
      - When supplied, this argument will restrict the facts collected
        to a given subset. Possible values for this argument include
        all, min, hardware, config, legacy, and interfaces. Can specify a
        list of values to include a larger subset. Values can also be used
        with an initial C(M(!)) to specify that a specific subset should
        not be collected.
    type: list
    required: false
    default: '!config'
  gather_network_resources:
    description:
      - When supplied, this argument will restrict the facts collected
        to a given subset. Possible values for this argument include
        all and the resources like interfaces, vlans etc.
        Can specify a list of values to include a larger subset. Values
        can also be used with an initial C(M(!)) to specify that a
        specific subset should not be collected.
    type: list
    choices:
      - all
      - log
      - sntp
      - vlan
      - linkagg
      - l2_interface
      - lldp
      - l3_interface
      - user
      - twamp
    required: false
"""

EXAMPLES = """
- name: Gather all facts
  dmos_facts:
    gather_subset: all
    gather_network_resources: all

- name: Collect only the l2_interface facts
  dmos_facts:
    gather_subset:
      - '!all'
      - '!min'
    gather_network_resources:
      - l2_interface

- name: Do not collect l2_interface facts
  dmos_facts:
    gather_network_resources:
      - '!l2_interface'

- name: Collect l2_interface and minimal default facts
  dmos_facts:
    gather_subset: min
    gather_network_resources: l2_interface
"""

RETURN = """
ansible_facts:
  description:
    - Returns the facts collect from the device
    - See the respective resource module parameters for the tree.
  returned: always
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.facts.facts import FactsArgs
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.facts import Facts


def main():
    """
    Main entry point for module execution

    :returns: ansible_facts
    """
    module = AnsibleModule(argument_spec=FactsArgs.argument_spec,
                           supports_check_mode=True)
    warnings = ['default value for `gather_subset` '
                'will be changed to `min` from `!config` v2.11 onwards']

    result = Facts(module).get_facts()

    ansible_facts, additional_warnings = result
    warnings.extend(additional_warnings)

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()
