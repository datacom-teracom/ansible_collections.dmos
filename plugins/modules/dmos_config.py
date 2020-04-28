#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for dmos_config
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: dmos_config
version_added: '2.9'
short_description: Execute configuration commands on dmos devices.
description: Execute configuration commands on dmos devices.
author:
  - Vinicius Kleinubing (@vgkleinubing) <vinicius.grubel@datacom.com.br>
  - LDS Labs (@lds-labs)
options:
  lines:
    description:
      - List of DmOS configuration commands to execute.
    required: false
"""

EXAMPLES = """
# Execute interface l3 test ipv4 address 10.0.0.1/24 command on DmOS device
- dmos_config:
    lines:
      - interface l3 test ipv4 address 10.0.0.1/24
      - interface l3 test ipv6 enable
"""

RETURN = """
changed:
  description: If configuration resulted in any change.
  type: str
  returned: always
  sample: True or False
changes:
  description: List of executed commands.
  type: list
  returned: always
  sample: ["interface l3 test ipv4 address 10.0.0.1/24"]
msg:
  description: Error message
  type: dict
  returned: on error
  sample: 'Aborted: reason'
response:
  description: The response of each executed commands
  type: list
  returned: always
  sample: ['Aborted: reason']
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.dmos import dmos_argument_spec
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.dmos import get_config, edit_config
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.utils.utils import get_command_list_from_curly_braces, get_command_list_diff


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        lines=dict(aliases=['commands'], type='list')
    )

    argument_spec.update(dmos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    result = {'changed': False}

    warnings = list()

    if module.params['lines']:
        config = get_config(module=module)
        command_list = get_command_list_from_curly_braces(output=config)
        candidates = get_command_list_diff(
            configs=command_list, candidates=module.params['lines'])

        if candidates:
            result['changes'] = candidates

            if not module.check_mode:
                response = edit_config(module=module, candidates=candidates)
                result['response'] = response['response']
                if response.get('error'):
                    module.fail_json(msg=response['error'])

            result['changed'] = True

    result['warnings'] = warnings
    module.exit_json(**result)


if __name__ == '__main__':
    main()
