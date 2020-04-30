#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_linkagg class
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


class Linkagg(ConfigBase):
    """
    The dmos_linkagg class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'linkagg',
    ]

    def __init__(self, module):
        super(Linkagg, self).__init__(module)

    def get_linkagg_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        linkagg_facts = facts['ansible_network_resources'].get('linkagg')
        if not linkagg_facts:
            return []
        return linkagg_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_linkagg_facts = self.get_linkagg_facts()
        commands.extend(self.set_config(existing_linkagg_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_linkagg_facts = self.get_linkagg_facts()

        result['before'] = existing_linkagg_facts
        if result['changed']:
            result['after'] = changed_linkagg_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_linkagg_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_linkagg_facts
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

        differ = DictDiffer(have, want, {'lag_id': [1], 'name': [3]})
        dict_diff = differ.deepdiff()

        sys_prio = dict_diff.get('sys_prio')
        if sys_prio is not None:
            commands.append(
                'link-aggregation system-priority {0}'.format(sys_prio))

        lag = dict_diff.get('lag')
        if lag is not None:
            for each_lag in lag:
                commands.extend(self._get_lag_commands(each_lag))

        return commands

    def _get_lag_commands(self, diff_dict):
        commands = []

        lag_id = diff_dict.get('lag_id')
        lag_cmd = 'link-aggregation interface lag {0}'.format(lag_id)

        if len(diff_dict) == 1:
            commands.append(lag_cmd)
            return commands

        admin_status = diff_dict.get('admin_status')
        if admin_status is not None:
            commands.append(
                '{0} administrative-status {1}'.format(lag_cmd, admin_status))

        description = diff_dict.get('description')
        if description is not None:
            commands.append(
                '{0} description "{1}"'.format(lag_cmd, description))

        interface = diff_dict.get('interface')
        if interface is not None:
            for each_interface in interface:
                commands.extend(self._get_interface_commands(
                    each_interface, lag_id))

        load_balance = diff_dict.get('load_balance')
        if load_balance is not None:
            commands.append(
                '{0} load-balance {1}'.format(lag_cmd, load_balance))

        max_active = diff_dict.get('max_active')
        if max_active is not None:
            commands.append(
                '{0} maximum-active links {1}'.format(lag_cmd, max_active))

        min_active = diff_dict.get('min_active')
        if min_active is not None:
            commands.append(
                '{0} minimum-active links {1}'.format(lag_cmd, min_active))

        mode = diff_dict.get('mode')
        if mode is not None:
            commands.append('{0} mode {1}'.format(lag_cmd, mode))

        period = diff_dict.get('period')
        if period is not None:
            commands.append('{0} period {1}'.format(lag_cmd, period))

        return commands

    def _get_interface_commands(self, diff_dict, lag_id):
        intf_name = diff_dict.get('name')
        intf_cmd = 'link-aggregation interface lag {0} interface {1}'.format(
            lag_id, intf_name)

        port_prio = diff_dict.get('port_prio')
        if port_prio is not None:
            intf_cmd += ' port-priority {0}'.format(port_prio)

        return [intf_cmd]

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no link-aggregation']

        differ = DictDiffer(have, want, {'lag_id': [1], 'name': [3]})
        dict_intsec = differ.deepintersect()

        sys_prio = dict_intsec.get('sys_prio')
        if sys_prio is not None:
            commands.append('no link-aggregation system-priority')

        lag = dict_intsec.get('lag')
        if lag is not None:
            for each_lag in lag:
                commands.extend(self._delete_lag_commands(each_lag))

        return commands

    def _delete_lag_commands(self, dict_intsec):
        commands = []

        lag_id = dict_intsec.get('lag_id')
        lag_cmd = 'no link-aggregation interface lag {0}'.format(lag_id)

        lag_n_keys = dict_intsec.get('n_keys')
        if lag_n_keys == 1:
            commands.append(lag_cmd)
            return commands

        admin_status = dict_intsec.get('admin_status')
        if admin_status is not None:
            commands.append('{0} administrative-status'.format(lag_cmd))

        description = dict_intsec.get('description')
        if description is not None:
            commands.append('{0} description'.format(lag_cmd))

        interface = dict_intsec.get('interface')
        if interface is not None:
            for each_interface in interface:
                commands.extend(self._delete_interface_commands(
                    each_interface, lag_id))

        load_balance = dict_intsec.get('load_balance')
        if load_balance is not None:
            commands.append('{0} load-balance'.format(lag_cmd))

        max_active = dict_intsec.get('max_active')
        if max_active is not None:
            commands.append('{0} maximum-active'.format(lag_cmd))

        min_active = dict_intsec.get('min_active')
        if min_active is not None:
            commands.append('{0} minimum-active'.format(lag_cmd))

        mode = dict_intsec.get('mode')
        if mode is not None:
            commands.append('{0} mode'.format(lag_cmd))

        period = dict_intsec.get('period')
        if period is not None:
            commands.append('{0} period'.format(lag_cmd))

        return commands

    def _delete_interface_commands(self, dict_intsec, lag_id):
        intf_name = dict_intsec.get('name')
        intf_cmd = 'no link-aggregation interface lag {0} interface {1}'.format(
            lag_id, intf_name)

        intf_n_keys = dict_intsec.get('n_keys')
        if intf_n_keys == 1:
            return [intf_cmd]

        port_prio = dict_intsec.get('port_prio')
        if port_prio is not None:
            intf_cmd += ' port-priority'

        return [intf_cmd]
