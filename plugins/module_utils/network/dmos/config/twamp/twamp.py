#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dmos_twamp class
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


class Twamp(ConfigBase):
    """
    The dmos_twamp class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'twamp',
    ]

    def __init__(self, module):
        super(Twamp, self).__init__(module)

    def get_twamp_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources)
        twamp_facts = facts['ansible_network_resources'].get('twamp')
        if not twamp_facts:
            return []
        return twamp_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_twamp_facts = self.get_twamp_facts()
        commands.extend(self.set_config(existing_twamp_facts))
        if commands:
            if not self._module.check_mode:
                response = self._connection.edit_config(commands)
                result['response'] = response['response']
                if response.get('error'):
                    self._module.fail_json(msg=response['error'])
            result['changed'] = True
        result['commands'] = commands

        changed_twamp_facts = self.get_twamp_facts()

        result['before'] = existing_twamp_facts
        if result['changed']:
            result['after'] = changed_twamp_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_twamp_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_twamp_facts
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

        differ = DictDiffer(
            have, want, {'address': [3], 'network': [3], 'id': [2, 4]})
        dict_diff = differ.deepdiff()

        reflector = dict_diff.get('reflector')
        if reflector is not None:
            reflector_cmd = 'oam twamp reflector'

            admin_status = reflector.get('admin_status')
            if admin_status is not None:
                commands.append(
                    '{0} administrative-status {1}'.format(reflector_cmd, admin_status))

            ipv4 = reflector.get('ipv4')
            if ipv4 is not None:
                client_address = ipv4.get('client_address')
                if client_address is not None:
                    for each in client_address:
                        address = each.get('address')
                        client_address_cmd = '{0} ipv4 client-address {1}'.format(
                            reflector_cmd, address)

                        if len(each) == 1:
                            commands.append(client_address_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_address_cmd, state))

                client_network = ipv4.get('client_network')
                if client_network is not None:
                    for each in client_network:
                        network = each.get('network')
                        client_network_cmd = '{0} ipv4 client-network {1}'.format(
                            reflector_cmd, network)

                        if len(each) == 1:
                            commands.append(client_network_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_network_cmd, state))

            ipv6 = reflector.get('ipv6')
            if ipv6 is not None:
                client_address = ipv6.get('client_address')
                if client_address is not None:
                    for each in client_address:
                        address = each.get('address')
                        client_address_cmd = '{0} ipv6 client-address {1}'.format(
                            reflector_cmd, address)

                        if len(each) == 1:
                            commands.append(client_address_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_address_cmd, state))

                client_network = ipv6.get('client_network')
                if client_network is not None:
                    for each in client_network:
                        network = each.get('network')
                        client_network_cmd = '{0} ipv6 client-network {1}'.format(
                            reflector_cmd, network)

                        if len(each) == 1:
                            commands.append(client_network_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_network_cmd, state))

            port = reflector.get('port')
            if port is not None:
                commands.append(
                    '{0} port {1}'.format(reflector_cmd, port))

        sender = dict_diff.get('sender')
        if sender is not None:
            sender_cmd = 'oam twamp sender'

            admin_status = sender.get('admin_status')
            if admin_status is not None:
                commands.append(
                    '{0} administrative-status {1}'.format(sender_cmd, admin_status))

            connection = sender.get('connection')
            if connection is not None:
                for each in connection:
                    conn_id = each.get('id')
                    conn_cmd = '{0} connection {1}'.format(sender_cmd, conn_id)

                    if len(each) == 1:
                        commands.append(conn_cmd)
                        continue

                    admin_status = each.get('admin_status')
                    if admin_status is not None:
                        commands.append(
                            '{0} administrative-status {1}'.format(conn_cmd, admin_status))

                    ipv4 = each.get('ipv4')
                    if ipv4 is not None:
                        source_address = ipv4.get('source_address')
                        if source_address is not None:
                            commands.append(
                                '{0} ipv4 source-address {1}'.format(conn_cmd, source_address))

                        target_address = ipv4.get('target_address')
                        if target_address is not None:
                            commands.append(
                                '{0} ipv4 target-address {1}'.format(conn_cmd, target_address))

                    ipv6 = each.get('ipv6')
                    if ipv6 is not None:
                        source_address = ipv6.get('source_address')
                        if source_address is not None:
                            commands.append(
                                '{0} ipv6 source-address {1}'.format(conn_cmd, source_address))

                        target_address = ipv6.get('target_address')
                        if target_address is not None:
                            commands.append(
                                '{0} ipv6 target-address {1}'.format(conn_cmd, target_address))

                    number_of_packets = each.get('number_of_packets')
                    if number_of_packets is not None:
                        commands.append(
                            '{0} number-of-packets {1}'.format(conn_cmd, number_of_packets))

                    server_port = each.get('server_port')
                    if server_port is not None:
                        commands.append(
                            '{0} server-port {1}'.format(conn_cmd, server_port))

                    test_interval = each.get('test_interval')
                    if test_interval is not None:
                        commands.append(
                            '{0} test-interval {1}'.format(conn_cmd, test_interval))

                    test_session = each.get('test_session')
                    if test_session is not None:
                        for each_test_session in test_session:
                            test_session_id = each_test_session.get('id')
                            test_session_cmd = '{0} test-session {1}'.format(
                                conn_cmd, test_session_id)

                            if len(each_test_session) == 1:
                                commands.append(test_session_cmd)
                                continue

                            test_session_ipv4 = each_test_session.get('ipv4')
                            if test_session_ipv4 is not None:
                                source_address = test_session_ipv4.get(
                                    'source_address')
                                if source_address is not None:
                                    commands.append(
                                        '{0} ipv4 source-address {1}'.format(test_session_cmd, source_address))

                                target_address = test_session_ipv4.get(
                                    'target_address')
                                if target_address is not None:
                                    commands.append(
                                        '{0} ipv4 target-address {1}'.format(test_session_cmd, target_address))

                            test_session_ipv6 = each_test_session.get('ipv6')
                            if test_session_ipv6 is not None:
                                source_address = test_session_ipv6.get(
                                    'source_address')
                                if source_address is not None:
                                    commands.append(
                                        '{0} ipv6 source-address {1}'.format(test_session_cmd, source_address))

                                target_address = test_session_ipv6.get(
                                    'target_address')
                                if target_address is not None:
                                    commands.append(
                                        '{0} ipv6 target-address {1}'.format(test_session_cmd, target_address))

                            dscp = each_test_session.get('dscp')
                            if dscp is not None:
                                commands.append(
                                    '{0} dscp {1}'.format(test_session_cmd, dscp))

                            max_port = each_test_session.get('max_port')
                            if max_port is not None:
                                commands.append(
                                    '{0} max-port {1}'.format(test_session_cmd, max_port))

                            min_port = each_test_session.get('min_port')
                            if min_port is not None:
                                commands.append(
                                    '{0} min-port {1}'.format(test_session_cmd, min_port))

                            packet_size = each_test_session.get('packet_size')
                            if packet_size is not None:
                                commands.append(
                                    '{0} packet-size {1}'.format(test_session_cmd, packet_size))

        return commands

    def _delete_config(self, want, have):
        """ Commands to delete configuration based on the want and have config

        :rtype: A list
        :returns: the commands necessary to delete the current configuration
                  of the provided objects
        """
        commands = []

        if not want and have:
            return ['no oam twamp']

        differ = DictDiffer(
            have, want, {'address': [3], 'network': [3], 'id': [2, 4]})
        dict_intsec = differ.deepintersect()

        reflector = dict_intsec.get('reflector')
        if reflector is not None:
            reflector_cmd = 'no oam twamp reflector'

            admin_status = reflector.get('admin_status')
            if admin_status is not None:
                commands.append(
                    '{0} administrative-status'.format(reflector_cmd))

            ipv4 = reflector.get('ipv4')
            if ipv4 is not None:
                client_address = ipv4.get('client_address')
                if client_address is not None:
                    for each in client_address:
                        address = each.get('address')
                        client_address_cmd = '{0} ipv4 client-address {1}'.format(
                            reflector_cmd, address)

                        client_address_n_keys = each.get('n_keys')
                        if client_address_n_keys == 1:
                            commands.append(client_address_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_address_cmd, state))

                client_network = ipv4.get('client_network')
                if client_network is not None:
                    for each in client_network:
                        network = each.get('network')
                        client_network_cmd = '{0} ipv4 client-network {1}'.format(
                            reflector_cmd, network)

                        client_network_n_keys = each.get('n_keys')
                        if client_network_n_keys == 1:
                            commands.append(client_network_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_network_cmd, state))

            ipv6 = reflector.get('ipv6')
            if ipv6 is not None:
                client_address = ipv6.get('client_address')
                if client_address is not None:
                    for each in client_address:
                        address = each.get('address')
                        client_address_cmd = '{0} ipv6 client-address {1}'.format(
                            reflector_cmd, address)

                        client_address_n_keys = each.get('n_keys')
                        if client_address_n_keys == 1:
                            commands.append(client_address_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_address_cmd, state))

                client_network = ipv6.get('client_network')
                if client_network is not None:
                    for each in client_network:
                        network = each.get('network')
                        client_network_cmd = '{0} ipv6 client-network {1}'.format(
                            reflector_cmd, network)

                        client_network_n_keys = each.get('n_keys')
                        if client_network_n_keys == 1:
                            commands.append(client_network_cmd)
                            continue

                        state = each.get('state')
                        if state is not None:
                            commands.append('{0} {1}'.format(
                                client_network_cmd, state))

            port = reflector.get('port')
            if port is not None:
                commands.append(
                    '{0} port'.format(reflector_cmd))

        sender = dict_intsec.get('sender')
        if sender is not None:
            sender_cmd = 'no oam twamp sender'

            admin_status = sender.get('admin_status')
            if admin_status is not None:
                commands.append(
                    '{0} administrative-status'.format(sender_cmd))

            connection = sender.get('connection')
            if connection is not None:
                for each in connection:
                    conn_id = each.get('id')
                    conn_cmd = '{0} connection {1}'.format(sender_cmd, conn_id)

                    conn_n_keys = each.get('n_keys')
                    if conn_n_keys == 1:
                        commands.append(conn_cmd)
                        continue

                    admin_status = each.get('admin_status')
                    if admin_status is not None:
                        commands.append(
                            '{0} administrative-status'.format(conn_cmd))

                    ipv4 = each.get('ipv4')
                    if ipv4 is not None:
                        source_address = ipv4.get('source_address')
                        if source_address is not None:
                            commands.append(
                                '{0} ipv4 source-address'.format(conn_cmd))

                        target_address = ipv4.get('target_address')
                        if target_address is not None:
                            commands.append(
                                '{0} ipv4 target-address'.format(conn_cmd))

                    ipv6 = each.get('ipv6')
                    if ipv6 is not None:
                        source_address = ipv6.get('source_address')
                        if source_address is not None:
                            commands.append(
                                '{0} ipv6 source-address'.format(conn_cmd))

                        target_address = ipv6.get('target_address')
                        if target_address is not None:
                            commands.append(
                                '{0} ipv6 target-address'.format(conn_cmd))

                    number_of_packets = each.get('number_of_packets')
                    if number_of_packets is not None:
                        commands.append(
                            '{0} number-of-packets'.format(conn_cmd))

                    server_port = each.get('server_port')
                    if server_port is not None:
                        commands.append(
                            '{0} server-port'.format(conn_cmd))

                    test_interval = each.get('test_interval')
                    if test_interval is not None:
                        commands.append(
                            '{0} test-interval'.format(conn_cmd))

                    test_session = each.get('test_session')
                    if test_session is not None:
                        for each_test_session in test_session:
                            test_session_id = each_test_session.get('id')
                            test_session_cmd = '{0} test-session {1}'.format(
                                conn_cmd, test_session_id)

                            test_session_n_keys = each_test_session.get('n_keys')
                            if test_session_n_keys == 1:
                                commands.append(test_session_cmd)
                                continue

                            test_session_ipv4 = each_test_session.get('ipv4')
                            if test_session_ipv4 is not None:
                                source_address = test_session_ipv4.get(
                                    'source_address')
                                if source_address is not None:
                                    commands.append(
                                        '{0} ipv4 source-address'.format(test_session_cmd))

                                target_address = test_session_ipv4.get(
                                    'target_address')
                                if target_address is not None:
                                    commands.append(
                                        '{0} ipv4 target-address'.format(test_session_cmd))

                            test_session_ipv6 = each_test_session.get('ipv6')
                            if test_session_ipv6 is not None:
                                source_address = test_session_ipv6.get(
                                    'source_address')
                                if source_address is not None:
                                    commands.append(
                                        '{0} ipv6 source-address'.format(test_session_cmd))

                                target_address = test_session_ipv6.get(
                                    'target_address')
                                if target_address is not None:
                                    commands.append(
                                        '{0} ipv6 target-address'.format(test_session_cmd))

                            dscp = each_test_session.get('dscp')
                            if dscp is not None:
                                commands.append(
                                    '{0} dscp'.format(test_session_cmd))

                            max_port = each_test_session.get('max_port')
                            if max_port is not None:
                                commands.append(
                                    '{0} max-port'.format(test_session_cmd))

                            min_port = each_test_session.get('min_port')
                            if min_port is not None:
                                commands.append(
                                    '{0} min-port'.format(test_session_cmd))

                            packet_size = each_test_session.get('packet_size')
                            if packet_size is not None:
                                commands.append(
                                    '{0} packet-size'.format(test_session_cmd))

        return commands
