#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_sntp class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import (
    ConfigBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.facts import (
    Facts,
)
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.utils.dict_differ import (
    DictDiffer,
)


class Sntp(ConfigBase):
    """
    The dmos_sntp class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'sntp',
    ]

    def __init__(self, module):
        super(Sntp, self).__init__(module)

    def get_sntp_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        sntp_facts = facts['ansible_network_resources'].get('sntp')
        if not sntp_facts:
            return []
        return sntp_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_sntp_facts = self.get_sntp_facts()
        commands.extend(self.set_config(existing_sntp_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_sntp_facts = self.get_sntp_facts()

        result['before'] = existing_sntp_facts
        if result['changed']:
            result['after'] = changed_sntp_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_sntp_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_sntp_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params['state']
        if state == 'overridden':
            commands = self._state_overridden(want, have)
        elif state == 'deleted':
            commands = self._state_deleted(want, have)
        elif state == 'merged':
            commands = self._state_merged(want, have)
        elif state == 'replaced':
            commands = self._state_replaced(want, have)
        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        if want:
            have = have[0] if have else dict()
            commands.extend(self._set_config(want[0], have))
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        want = want[0] if want else dict()
        have = have[0] if have else dict()
        commands.extend(self._delete_config(want, have))
        return commands

    def _set_config(self, want, have):
        """ Commands to set configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to set the current configuration
                  of the provided objects
        """
        commands = []

        differ = DictDiffer(have, want, {'id': [1], 'address': [1]})
        dict_diff = differ.deepdiff()

        auth = dict_diff.get('auth')
        if auth is not None:
            commands.append(
                '{0} sntp authenticate'.format('' if auth else 'no').strip())

        auth_key = dict_diff.get('auth_key')
        if auth_key is not None:
            for each in auth_key:
                each = dict(each)
                id_value = each.get('id')
                auth_key_cmd = 'sntp authentication-key {0}'.format(id_value)

                if len(each) == 1:
                    commands.append(auth_key_cmd)
                    continue

                pass_value = each.get('pass')
                if pass_value is not None:
                    auth_key_cmd += ' md5 {0}'.format(pass_value)
                commands.append(auth_key_cmd)

        client = dict_diff.get('client')
        if client is not None:
            commands.append('{0} sntp client'.format('' if client else 'no').strip())

        max_poll = dict_diff.get('max_poll')
        if max_poll is not None:
            commands.append('sntp max-poll {0}'.format(max_poll))

        min_poll = dict_diff.get('min_poll')
        if min_poll is not None:
            commands.append('sntp min-poll {0}'.format(min_poll))

        server = dict_diff.get('server')
        if server is not None:
            for each in server:
                each = dict(each)
                address = each.get('address')
                server_cmd = 'sntp server {0}'.format(address)

                if len(each) == 1:
                    commands.append(server_cmd)
                    continue

                key_id = each.get('key_id')
                if key_id is not None:
                    server_cmd += ' key {0}'.format(key_id)
                commands.append(server_cmd)

        source = dict_diff.get('source')
        if source is not None:
            source = dict(source)
            ipv4 = source.get('ipv4')
            if ipv4 is not None:
                commands.append(
                    'sntp source ipv4 address {0}'.format(ipv4))
            ipv6 = source.get('ipv6')
            if ipv6 is not None:
                commands.append(
                    'sntp source ipv6 address {0}'.format(ipv6))

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no sntp']

        differ = DictDiffer(have, want, {'id': [1], 'address': [1]})
        dict_intsec = differ.deepintersect()

        auth = dict_intsec.get('auth')
        if auth is not None:
            commands.append('no sntp authenticate')

        auth_key = dict_intsec.get('auth_key')
        if auth_key is not None:
            for each in auth_key:
                each = dict(each)
                id_value = each.get('id')
                auth_key_cmd = 'no sntp authentication-key {0}'.format(
                    id_value)

                auth_key_n_keys = each.get('n_keys')
                if auth_key_n_keys == 1:
                    commands.append(auth_key_cmd)
                    continue

        client = dict_intsec.get('client')
        if client is not None:
            commands.append('no sntp client')

        max_poll = dict_intsec.get('max_poll')
        if max_poll is not None:
            commands.append('no sntp max-poll')

        min_poll = dict_intsec.get('min_poll')
        if min_poll is not None:
            commands.append('no sntp min-poll')

        server = dict_intsec.get('server')
        if server is not None:
            for each in server:
                each = dict(each)
                address = each.get('address')
                server_cmd = 'no sntp server {0}'.format(address)

                server_n_keys = each.get('n_keys')
                if server_n_keys == 1:
                    commands.append(server_cmd)
                    continue

                key_id = each.get('key_id')
                if key_id is not None:
                    server_cmd += ' key'
                commands.append(server_cmd)

        source = dict_intsec.get('source')
        if source is not None:
            source = dict(source)
            ipv4 = source.get('ipv4')
            if ipv4 is not None:
                commands.append('no sntp source ipv4')
            ipv6 = source.get('ipv6')
            if ipv6 is not None:
                commands.append('no sntp source ipv6')

        return commands
