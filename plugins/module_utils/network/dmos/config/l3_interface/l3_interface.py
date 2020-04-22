#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_l3_interface class
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


class L3_interface(ConfigBase):
    """
    The dmos_l3_interface class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'l3_interface',
    ]

    def __init__(self, module):
        super(L3_interface, self).__init__(module)

    def get_l3_interface_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        l3_interface_facts = facts['ansible_network_resources'].get(
            'l3_interface')
        if not l3_interface_facts:
            return []
        return l3_interface_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_l3_interface_facts = self.get_l3_interface_facts()
        commands.extend(self.set_config(existing_l3_interface_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_l3_interface_facts = self.get_l3_interface_facts()

        result['before'] = existing_l3_interface_facts
        if result['changed']:
            result['after'] = changed_l3_interface_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_l3_interface_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_l3_interface_facts
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

        differ = DictDiffer(have, want, {'name': [1], 'ip': [5]})

        dict_diff = differ.deepdiff()
        for diff in dict_diff:
            intf_name = diff.get('name')
            intf_cmd = 'interface l3 {0}'.format(intf_name)

            if len(diff) == 1:
                commands.append(intf_cmd)
                continue

            description = diff.get('description')
            if description is not None:
                commands.append('{0} description "{1}"'.format(
                    intf_cmd, description))

            ip_mtu = diff.get('ip_mtu')
            if ip_mtu is not None:
                commands.append('{0} ip-mtu {1}'.format(intf_cmd, ip_mtu))

            lower_layer_if = diff.get('lower_layer_if')
            if lower_layer_if is not None:
                commands.append(
                    '{0} lower-layer-if vlan {1}'.format(intf_cmd, lower_layer_if))

            vlan_link_detect = diff.get('vlan_link_detect')
            if vlan_link_detect is not None:
                commands.append('{0} vlan-link-detect {1}'.format(intf_cmd,
                                                                  'enabled' if vlan_link_detect else 'disabled'))

            vrf = diff.get('vrf')
            if vrf is not None:
                commands.append('{0} vrf {1}'.format(intf_cmd, vrf))

            ipv4 = diff.get('ipv4')
            if ipv4 is not None:
                address = ipv4.get('address')
                if address is not None:
                    commands.append(
                        '{0} ipv4 address {1}'.format(intf_cmd, address))

                secondary = ipv4.get('secondary')
                if secondary is not None:
                    for each in secondary:
                        commands.append(
                            '{0} ipv4 address secondary {1}'.format(intf_cmd, each))

            ipv6 = diff.get('ipv6')
            if ipv6 is not None:
                enable = ipv6.get('enable')
                if enable is not None:
                    commands.append('{0} {1} ipv6 enable'.format(
                        '' if enable else 'no', intf_cmd).strip())

                address = ipv6.get('address')
                if address is not None:
                    for each in address:
                        commands.append(
                            '{0} ipv6 address {1}'.format(intf_cmd, each))

                nd_ra = ipv6.get('nd_ra')
                if nd_ra is not None:
                    nd_ra_cmd = '{0} ipv6 nd ra'.format(intf_cmd)

                    lifetime = nd_ra.get('lifetime')
                    if lifetime is not None:
                        commands.append(
                            '{0} lifetime {1}'.format(nd_ra_cmd, lifetime))

                    max_interval = nd_ra.get('max_interval')
                    if max_interval is not None:
                        commands.append(
                            '{0} max-interval {1}'.format(nd_ra_cmd, max_interval))

                    min_interval = nd_ra.get('min_interval')
                    if min_interval is not None:
                        commands.append(
                            '{0} min-interval {1}'.format(nd_ra_cmd, min_interval))

                    prefix = nd_ra.get('prefix')
                    if prefix is not None:
                        for each in prefix:
                            each = dict(each)
                            prefix_ip = each.get('ip')
                            prefix_cmd = '{0} prefix {1}'.format(
                                nd_ra_cmd, prefix_ip)

                            if len(each) == 1:
                                commands.append(prefix_cmd)
                                continue

                            no_advertise = each.get('no_advertise')
                            if no_advertise is not None:
                                commands.append(
                                    '{0} {1} no-advertise'.format('' if no_advertise else 'no', prefix_cmd).strip())

                            no_autoconfig = each.get('no_autoconfig')
                            if no_autoconfig is not None:
                                commands.append(
                                    '{0} {1} no-autoconfig'.format('' if no_autoconfig else 'no', prefix_cmd).strip())

                            off_link = each.get('off_link')
                            if off_link is not None:
                                commands.append(
                                    '{0} {1} off-link'.format('' if off_link else 'no', prefix_cmd).strip())

                    suppress = nd_ra.get('suppress')
                    if suppress is not None:
                        commands.append('{0} {1} suppress'.format(
                            '' if suppress else 'no', nd_ra_cmd).strip())

                    mtu_suppress = nd_ra.get('mtu_suppress')
                    if mtu_suppress is not None:
                        commands.append('{0} {1} mtu suppress'.format(
                            '' if mtu_suppress else 'no', nd_ra_cmd).strip())

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no interface l3']

        differ = DictDiffer(have, want, {'name': [1], 'ip': [5]})
        dict_intsec = differ.deepintersect()

        for diff in dict_intsec:
            intf_name = diff.get('name')
            intf_cmd = 'no interface l3 {0}'.format(intf_name)

            intf_n_keys = diff.get('n_keys')
            if intf_n_keys == 1:
                commands.append(intf_cmd)
                continue

            description = diff.get('description')
            if description is not None:
                commands.append('{0} description'.format(intf_cmd))

            ip_mtu = diff.get('ip_mtu')
            if ip_mtu is not None:
                commands.append('{0} ip-mtu'.format(intf_cmd))

            lower_layer_if = diff.get('lower_layer_if')
            if lower_layer_if is not None:
                commands.append('{0} lower-layer-if vlan'.format(intf_cmd))

            # Ignoring vlan link detect deletion since its not possible, always returns error
            # vlan_link_detect = diff.get('vlan_link_detect')
            # if vlan_link_detect is not None:
            #     commands.append('{0} vlan-link-detect'.format(intf_cmd))

            vrf = diff.get('vrf')
            if vrf is not None:
                commands.append('{0} vrf'.format(intf_cmd))

            ipv4 = diff.get('ipv4')
            if ipv4 is not None:
                address = ipv4.get('address')
                if address is not None:
                    commands.append(
                        '{0} ipv4 address {1}'.format(intf_cmd, address))

                secondary = ipv4.get('secondary')
                if secondary is not None:
                    for each in secondary:
                        commands.append(
                            '{0} ipv4 address secondary {1}'.format(intf_cmd, each))

            ipv6 = diff.get('ipv6')
            if ipv6 is not None:
                address = ipv6.get('address')
                if address is not None:
                    for each in address:
                        commands.append(
                            '{0} ipv6 address {1}'.format(intf_cmd, each))

                nd_ra = ipv6.get('nd_ra')
                if nd_ra is not None:
                    nd_ra_cmd = '{0} ipv6 nd ra'.format(intf_cmd)

                    lifetime = nd_ra.get('lifetime')
                    if lifetime is not None:
                        commands.append('{0} lifetime'.format(nd_ra_cmd))

                    max_interval = nd_ra.get('max_interval')
                    if max_interval is not None:
                        commands.append('{0} max-interval'.format(nd_ra_cmd))

                    min_interval = nd_ra.get('min_interval')
                    if min_interval is not None:
                        commands.append('{0} min-interval'.format(nd_ra_cmd))

                    prefix = nd_ra.get('prefix')
                    if prefix is not None:
                        for each in prefix:
                            each = dict(each)
                            prefix_ip = each.get('ip')
                            prefix_cmd = '{0} prefix {1}'.format(
                                nd_ra_cmd, prefix_ip)

                            prefix_n_keys = each.get('n_keys')
                            if prefix_n_keys == 1:
                                commands.append(prefix_cmd)
                                continue

                            no_advertise = each.get('no_advertise')
                            if no_advertise is not None:
                                commands.append(
                                    '{0} no-advertise'.format(prefix_cmd))

                            no_autoconfig = each.get('no_autoconfig')
                            if no_autoconfig is not None:
                                commands.append(
                                    '{0} no-autoconfig'.format(prefix_cmd))

                            off_link = each.get('off_link')
                            if off_link is not None:
                                commands.append(
                                    '{0} off-link'.format(prefix_cmd))

                    suppress = nd_ra.get('suppress')
                    if suppress is not None:
                        commands.append('{0} suppress'.format(nd_ra_cmd))

                    mtu_suppress = nd_ra.get('mtu_suppress')
                    if mtu_suppress is not None:
                        commands.append('{0} mtu suppress'.format(nd_ra_cmd))

                enable = ipv6.get('enable')
                if enable is not None:
                    commands.append('{0} ipv6 enable'.format(intf_cmd))

        return commands
