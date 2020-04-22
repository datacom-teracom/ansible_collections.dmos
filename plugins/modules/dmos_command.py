#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for dmos_command
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
module: dmos_command
version_added: '2.10'
short_description: Execute show commands on dmos devices.
description: Execute show commands on dmos devices.
author:
  - Vinicius Kleinubing (@vgkleinubing) <vinicius.grubel@datacom.com.br>
  - LDS Labs (@lds-labs)
notes:
  - Tested against DmOS version 5.2.0.
options:
  commands:
    description:
      - List of DmOS show command to execute.
    type: list
    required: true
  match:
    description:
      - Check if lines as present in output
    type: str
    choices: ['exact']
    required: false
  lines:
    description:
      - List of lines to match
    type: list
    required: false
"""

EXAMPLES = """
# Execute show running-config interface l3 command on DmOS device
- dmos_command:
    commands:
      - show running-config interface l3
      - show oam twamp sender
"""

RETURN = """
changed:
  description: Always false.
  type: str
  returned: always
  sample: True or False
stdout:
  description: Raw output of command.
  type: str
  returned: always
  sample: ["interface l3 test\n ipv4 address 10.0.0.1/24\n!"]
stdout_lines:
  description: Raw output of command splitted in lines.
  type: list
  returned: always
  sample: ["interface l3 test", "ipv4 address 10.0.0.1/24", "!"]
warnings:
  description: List of warnings generates in execution.
  type: list
  returned: Always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    transform_commands,
    to_lines,
)
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.dmos import dmos_argument_spec, run_commands


def parse_commands(module, warnings):
    commands = transform_commands(module)

    if module.check_mode:
        for item in list(commands):
            if not item['command'].startswith('show'):
                warnings.append(
                    'Only show commands are supported when using check mode, not '
                    'executing %s' % item['command']
                )
                commands.remove(item)

    return commands


def main():
    """main entry point for module execution
    """
    argument_spec = dict(
        commands=dict(type='list', required=True),
        match=dict(type='str', choices=['exact']),
        lines=dict(type='list'),
    )

    argument_spec.update(dmos_argument_spec)

    required_if = [('match', 'exact', ['lines'])]

    module = AnsibleModule(argument_spec=argument_spec,
                           required_if=required_if,
                           supports_check_mode=True)

    warnings = list()
    commands = parse_commands(module, warnings)

    responses = run_commands(module, commands)

    if module.params['match']:
        for line in module.params['lines']:
            if line not in responses:
                module.fail_json(msg="didn't match the lines")
                return

    result = {'changed': False, 'warnings': warnings}
    result.update({
        'stdout': responses,
        'stdout_lines': list(to_lines(responses)),
    })

    module.exit_json(**result)


if __name__ == '__main__':
    main()
