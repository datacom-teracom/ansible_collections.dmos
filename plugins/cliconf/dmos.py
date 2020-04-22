#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
author:
  - Vinicius Kleinubing (@vgkleinubing) <vinicius.grubel@datacom.com.br>
  - LDS Labs (@lds-labs)
cliconf: dmos
short_description: Use junos cliconf to run command on Juniper Junos OS platform
description:
  - This dmos plugin provides low level abstraction apis for
    sending and receiving CLI commands from Datacom DmOS network devices.
version_added: "2.10"
"""


import re
import time
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import dumps
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase


class Cliconf(CliconfBase):

    def get_config(self):
        return self.send_command('show running-config | details | display curly-braces | nomore')

    def edit_config(self, candidates=None, commit=True, replace=None, comment=None):
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(
            operations, candidates, commit, replace, comment)

        results = []
        requests = []
        if commit:
            self.send_command('config')
            for line in to_list(candidates):
                if not isinstance(line, Mapping):
                    line = {'command': line}

                cmd = line['command']
                if cmd != 'end' and cmd[0] != '!':
                    response = self.send_command(**line)
                    if response != '':
                        results.append(response)
                    requests.append(cmd)

            commit_msg = self.send_command('commit')
            if commit_msg != 'Commit complete.' and commit_msg != '% No modifications to commit.':
                resp['error'] = commit_msg
                self.send_command('abort')
            else:
                self.send_command('end')
        else:
            raise ValueError('check mode is not supported')

        resp['request'] = requests
        resp['response'] = results
        return resp

    def get(self, command=None, prompt=None, answer=None, sendonly=False, output=None, newline=True, check_all=False):
        if not command:
            raise ValueError('must provide value of command to execute')
        if output:
            raise ValueError(
                "'output' value %s is not supported for get" % output)

        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'dmos'
        reply = self.get(command='show platform')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'Version (\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1).strip(',')

        return device_info

    def get_device_operations(self):
        return {
            'supports_diff_replace': True,
            'supports_commit': False,
            'supports_rollback': False,
            'supports_defaults': True,
            'supports_onbox_diff': False,
            'supports_commit_comment': False,
            'supports_multiline_delimiter': True,
            'supports_diff_match': True,
            'supports_diff_ignore_lines': True,
            'supports_generate_diff': True,
            'supports_replace': False
        }

    def get_option_values(self):
        return {
            'format': ['text'],
            'diff_match': ['line', 'strict', 'exact', 'none'],
            'diff_replace': ['line', 'block'],
            'output': []
        }

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result['device_operations'] = self.get_device_operations()
        result.update(self.get_option_values())
        return json.dumps(result)

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {'command': cmd}

            output = cmd.pop('output', None)
            if output:
                raise ValueError(
                    "'output' value %s is not supported for run_commands" % output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, 'err', to_text(e))

            responses.append(out)

        return responses
