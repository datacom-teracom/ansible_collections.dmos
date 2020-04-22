#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_l2_interface class
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


class L2_interface(ConfigBase):
    """
    The dmos_l2_interface class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'l2_interface',
    ]

    def __init__(self, module):
        super(L2_interface, self).__init__(module)

    def get_l2_interface_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        l2_interface_facts = facts['ansible_network_resources'].get('l2_interface')
        if not l2_interface_facts:
            return []
        return l2_interface_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_l2_interface_facts = self.get_l2_interface_facts()
        commands.extend(self.set_config(existing_l2_interface_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_l2_interface_facts = self.get_l2_interface_facts()

        result['before'] = existing_l2_interface_facts
        if result['changed']:
            result['after'] = changed_l2_interface_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_l2_interface_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_l2_interface_facts
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

        differ = DictDiffer(have, want, {'interface_name': [1], 'traffic': [3]})

        dict_diff = differ.deepdiff()
        for diff in dict_diff:
            interface_name = diff.get('interface_name')
            switchport_cmd = 'switchport interface {0}'.format(interface_name)

            if len(diff) == 1:
                commands.append(switchport_cmd)
                continue

            native_vlan_id = diff.get('native_vlan_id')
            if native_vlan_id is not None:
                commands.append(
                    '{0} native-vlan vlan-id {1}'.format(switchport_cmd, native_vlan_id))

            qinq = diff.get('qinq')
            if qinq is not None:
                commands.append(
                    '{0} {1} qinq'.format('' if qinq else 'no', switchport_cmd).strip())

            storm_control = diff.get('storm_control')
            if storm_control is not None:
                for each in storm_control:
                    each = dict(each)
                    traffic = each.get('traffic')
                    percent = each.get('percent')
                    storm_control_cmd = '{0} storm-control {1} {2}'.format(
                        switchport_cmd, traffic, percent)

                    commands.append(storm_control_cmd)

            tpid = diff.get('tpid')
            if tpid is not None:
                commands.append(
                    '{0} tpid {1}'.format(switchport_cmd, tpid))

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no switchport']

        differ = DictDiffer(have, want, {'interface_name': [1], 'traffic': [3]})
        dict_intsec = differ.deepintersect()

        for diff in dict_intsec:
            interface_name = diff.get('interface_name')
            switchport_cmd = 'no switchport interface {0}'.format(
                interface_name)

            switchport_n_keys = diff.get('n_keys')
            if switchport_n_keys == 1:
                commands.append(switchport_cmd)
                continue

            native_vlan_id = diff.get('native_vlan_id')
            if native_vlan_id is not None:
                commands.append(
                    '{0} native-vlan'.format(switchport_cmd))

            qinq = diff.get('qinq')
            if qinq is not None:
                commands.append(
                    '{0} qinq'.format(switchport_cmd))

            storm_control = diff.get('storm_control')
            if storm_control is not None:
                for each in storm_control:
                    each = dict(each)
                    traffic = each.get('traffic')
                    storm_control_cmd = '{0} storm-control {1}'.format(
                        switchport_cmd, traffic)

                    commands.append(storm_control_cmd)

            tpid = diff.get('tpid')
            if tpid is not None:
                commands.append(
                    '{0} tpid'.format(switchport_cmd))

        return commands
