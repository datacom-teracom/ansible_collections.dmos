#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_lldp class
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


class Lldp(ConfigBase):
    """
    The dmos_lldp class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lldp',
    ]

    def __init__(self, module):
        super(Lldp, self).__init__(module)

    def get_lldp_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        lldp_facts = facts['ansible_network_resources'].get('lldp')
        if not lldp_facts:
            return []
        return lldp_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_lldp_facts = self.get_lldp_facts()
        commands.extend(self.set_config(existing_lldp_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_lldp_facts = self.get_lldp_facts()

        result['before'] = existing_lldp_facts
        if result['changed']:
            result['after'] = changed_lldp_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_lldp_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lldp_facts
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

        differ = DictDiffer(have, want, {'name': [1]})
        dict_diff = differ.deepdiff()

        interface = dict_diff.get('interface')
        if interface is not None:
            for each in interface:
                each = dict(each)
                intf_name = each.get('name')
                intf_cmd = 'lldp interface {0}'.format(intf_name)

                if len(each) == 1:
                    commands.append(intf_cmd)
                    continue

                admin_status = each.get('admin_status')
                if admin_status is not None:
                    commands.append(
                        '{0} admin-status {1}'.format(intf_cmd, admin_status))

                notification = each.get('notification')
                if notification is not None:
                    commands.append('{0} {1} notification'.format(
                        '' if notification else 'no', intf_cmd).strip())

                tlv_port_description = each.get('tlv_port_description')
                if tlv_port_description is not None:
                    commands.append(
                        '{0} {1} tlvs-tx port-description'.format('' if tlv_port_description else 'no', intf_cmd).strip())

                tlv_system_capabilities = each.get('tlv_system_capabilities')
                if tlv_system_capabilities is not None:
                    commands.append(
                        '{0} {1} tlvs-tx system-capabilities'.format('' if tlv_system_capabilities else 'no', intf_cmd).strip())

                tlv_system_description = each.get('tlv_system_description')
                if tlv_system_description is not None:
                    commands.append(
                        '{0} {1} tlvs-tx system-description'.format('' if tlv_system_description else 'no', intf_cmd).strip())

                tlv_system_name = each.get('tlv_system_name')
                if tlv_system_name is not None:
                    commands.append(
                        '{0} {1} tlvs-tx system-name'.format('' if tlv_system_name else 'no', intf_cmd).strip())

        msg_fast_tx = dict_diff.get('msg_fast_tx')
        if msg_fast_tx is not None:
            commands.append('lldp message-fast-tx {0}'.format(msg_fast_tx))

        msg_tx_hold_multi = dict_diff.get('msg_tx_hold_multi')
        if msg_tx_hold_multi is not None:
            commands.append(
                'lldp message-tx-hold-multiplier {0}'.format(msg_tx_hold_multi))

        msg_tx_interval = dict_diff.get('msg_tx_interval')
        if msg_tx_interval is not None:
            commands.append(
                'lldp message-tx-interval {0}'.format(msg_tx_interval))

        notification_interval = dict_diff.get('notification_interval')
        if notification_interval is not None:
            commands.append(
                'lldp notification-interval {0}'.format(notification_interval))

        reinit_delay = dict_diff.get('reinit_delay')
        if reinit_delay is not None:
            commands.append('lldp reinit-delay {0}'.format(reinit_delay))

        tx_credit_max = dict_diff.get('tx_credit_max')
        if tx_credit_max is not None:
            commands.append('lldp tx-credit-max  {0}'.format(tx_credit_max))

        tx_fast_init = dict_diff.get('tx_fast_init')
        if tx_fast_init is not None:
            commands.append('lldp tx-fast-init {0}'.format(tx_fast_init))

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no lldp']

        differ = DictDiffer(have, want, {'name': [1]})
        dict_intsec = differ.deepintersect()

        interface = dict_intsec.get('interface')
        if interface is not None:
            for each in interface:
                each = dict(each)
                intf_name = each.get('name')
                intf_cmd = 'no lldp interface {0}'.format(intf_name)

                intf_n_keys = each.get('n_keys')
                if intf_n_keys == 1:
                    commands.append(intf_cmd)
                    continue

                admin_status = each.get('admin_status')
                if admin_status is not None:
                    commands.append('{0} admin-status'.format(intf_cmd))

                notification = each.get('notification')
                if notification is not None:
                    commands.append('{0} notification'.format(intf_cmd))

                tlv_port_description = each.get('tlv_port_description')
                if tlv_port_description is not None:
                    commands.append(
                        '{0} tlvs-tx port-description'.format(intf_cmd))

                tlv_system_capabilities = each.get('tlv_system_capabilities')
                if tlv_system_capabilities is not None:
                    commands.append(
                        '{0} tlvs-tx system-capabilities'.format(intf_cmd))

                tlv_system_description = each.get('tlv_system_description')
                if tlv_system_description is not None:
                    commands.append(
                        '{0} tlvs-tx system-description'.format(intf_cmd))

                tlv_system_name = each.get('tlv_system_name')
                if tlv_system_name is not None:
                    commands.append('{0} tlvs-tx system-name'.format(intf_cmd))

        msg_fast_tx = dict_intsec.get('msg_fast_tx')
        if msg_fast_tx is not None:
            commands.append('no lldp message-fast-tx')

        msg_tx_hold_multi = dict_intsec.get('msg_tx_hold_multi')
        if msg_tx_hold_multi is not None:
            commands.append(
                'no lldp message-tx-hold-multiplier')

        msg_tx_interval = dict_intsec.get('msg_tx_interval')
        if msg_tx_interval is not None:
            commands.append(
                'no lldp message-tx-interval')

        notification_interval = dict_intsec.get('notification_interval')
        if notification_interval is not None:
            commands.append(
                'no lldp notification-interval')

        reinit_delay = dict_intsec.get('reinit_delay')
        if reinit_delay is not None:
            commands.append('no lldp reinit-delay')

        tx_credit_max = dict_intsec.get('tx_credit_max')
        if tx_credit_max is not None:
            commands.append('no lldp tx-credit-max')

        tx_fast_init = dict_intsec.get('tx_fast_init')
        if tx_fast_init is not None:
            commands.append('no lldp tx-fast-init')

        return commands
