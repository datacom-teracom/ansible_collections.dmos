#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_user class
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


class User(ConfigBase):
    """
    The dmos_user class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'user',
    ]

    def __init__(self, module):
        super(User, self).__init__(module)

    def get_user_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        user_facts = facts['ansible_network_resources'].get('user')
        if not user_facts:
            return []
        return user_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_user_facts = self.get_user_facts()
        commands.extend(self.set_config(existing_user_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_user_facts = self.get_user_facts()

        result['before'] = existing_user_facts
        if result['changed']:
            result['after'] = changed_user_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_user_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_user_facts
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
            have = have if have else []
            commands.extend(self._set_config(want, have))
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        if want:
            have = have if have else []
            commands.extend(self._delete_config(want, have))
        return commands

    def _set_config(self, want, have):
        """ Commands to set configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to set the current configuration
                  of the provided objects
        """
        commands = []

        differ = DictDiffer(have, want, {'name': [0, 1]})

        dict_diff = differ.deepdiff()

        for user_config in dict_diff:
            cmd = ''
            name = user_config.get('name')
            if name is not None:
                cmd = 'user {0}'.format(name)
            alias = user_config.get('alias')
            if alias is not None:
                for each in alias:
                    alias_name = each.get('name')
                    expansion = each.get('expansion')
                    if alias_name is None:
                        continue
                    temp_cmd = '{0} alias {1}'.format(cmd, alias_name)
                    if expansion is not None:
                        temp_cmd = '{0} expansion {1}'.format(temp_cmd, expansion)
                    commands.append(temp_cmd)

            description = user_config.get('description')
            if description is not None:
                commands.append('{0} description {1}'.format(cmd, description))
            session = user_config.get('session')
            if session is not None:
                for key, value in session.items():
                    if isinstance(value, bool):
                        value = str(value).lower()
                    commands.append('{0} session {1} {2}'.format(cmd, key.replace('_', '-'), value))

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no user']

        differ = DictDiffer(have, want, {'name': [0, 1]})
        dict_intsec = differ.deepintersect()
        for user in dict_intsec:
            name = user.get('name')
            if name is None:
                continue
            no_user_cmd = 'no user {0}'.format(name)
            if user.get('n_keys') == 1:
                commands.append(no_user_cmd)
                continue
            alias = user.get('alias')
            if alias is not None:
                for each in alias:
                    alias_name = each.get('name')
                    if alias_name is None:
                        continue
                    temp_cmd = '{0} alias {1}'.format(no_user_cmd, alias_name)
                    commands.append(temp_cmd)

            description = user.get('description')
            if description is not None:
                commands.append('{0} description'.format(no_user_cmd))
            session = user.get('session')
            if session is not None:
                for key in session.keys():
                    if key == 'n_keys':
                        continue
                    commands.append('{0} session {1}'.format(no_user_cmd, key.replace('_', '-')))

        return commands
