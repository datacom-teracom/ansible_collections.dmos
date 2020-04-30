#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_vlan class
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


class Vlan(ConfigBase):
    """
    The dmos_vlan class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'vlan',
    ]

    def __init__(self, module):
        super(Vlan, self).__init__(module)

    def get_vlan_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        vlan_facts = facts['ansible_network_resources'].get('vlan')
        if not vlan_facts:
            return []
        return vlan_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_vlan_facts = self.get_vlan_facts()
        commands.extend(self.set_config(existing_vlan_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_vlan_facts = self.get_vlan_facts()

        result['before'] = existing_vlan_facts
        if result['changed']:
            result['after'] = changed_vlan_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_vlan_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_vlan_facts
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
        want = want if want else []
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

        differ = DictDiffer(have, want, {'vlan_id': [1], 'name': [3]})

        dict_diff = differ.deepdiff()
        for diff in dict_diff:
            vlan_id = diff.get('vlan_id')
            vlan_cmd = 'dot1q vlan {0}'.format(vlan_id)

            if len(diff) == 1:
                commands.append(vlan_cmd)
                continue

            name = diff.get('name')
            if name is not None:
                commands.append('{0} name "{1}"'.format(vlan_cmd, name))

            interface = diff.get('interface')
            if interface is not None:
                for each in interface:
                    each = dict(each)
                    intf_name = each.get('name')
                    intf_cmd = '{0} interface {1}'.format(vlan_cmd, intf_name)

                    tagged = each.get('tagged')
                    if tagged is not None:
                        intf_cmd += ' tagged' if tagged else ' untagged'
                    commands.append(intf_cmd)

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no dot1q']

        differ = DictDiffer(have, want, {'vlan_id': [1], 'name': [3]})
        dict_intsec = differ.deepintersect()

        for diff in dict_intsec:
            vlan_id = diff.get('vlan_id')
            vlan_cmd = 'no dot1q vlan {0}'.format(vlan_id)

            vlan_n_keys = diff.get('n_keys')
            if vlan_n_keys == 1:
                commands.append(vlan_cmd)
                continue

            name = diff.get('name')
            if name is not None:
                commands.append('{0} name'.format(vlan_cmd))

            interface = diff.get('interface')
            if interface is not None:
                for each in interface:
                    each = dict(each)
                    intf_name = each.get('name')
                    intf_cmd = '{0} interface {1}'.format(vlan_cmd, intf_name)

                    intf_n_keys = each.get('n_keys')
                    if intf_n_keys == 1:
                        commands.append(intf_cmd)
                        continue

                    tagged = each.get('tagged')
                    if tagged is not None:
                        intf_cmd += ' tagged' if tagged else ' untagged'
                    commands.append(intf_cmd)

        return commands
