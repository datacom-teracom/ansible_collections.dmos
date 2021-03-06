#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The arg spec for the dmos_l3_interface module
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class L3_interfaceArgs(object):  # pylint: disable=R0903
    """The arg spec for the dmos_l3_interface module
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {'config': {'elements': 'dict',
                                'options': {'description': {'type': 'str'},
                                            'ip_mtu': {'type': 'int'},
                                            'ipv4': {'options': {'address': {'type': 'str'},
                                                                 'secondary': {'elements': 'str',
                                                                               'type': 'list'}},
                                                     'type': 'dict'},
                                            'ipv6': {'options': {'address': {'elements': 'str',
                                                                             'type': 'list'},
                                                                 'enable': {'type': 'bool'},
                                                                 'nd_ra': {'options': {'lifetime': {'type': 'int'},
                                                                                       'max_interval': {'type': 'int'},
                                                                                       'min_interval': {'type': 'int'},
                                                                                       'mtu_suppress': {'type': 'bool'},
                                                                                       'prefix': {'elements': 'dict',
                                                                                                  'options': {'ip': {'required': True,
                                                                                                                     'type': 'str'},
                                                                                                              'no_advertise': {'type': 'bool'},
                                                                                                              'no_autoconfig': {'type': 'bool'},
                                                                                                              'off_link': {'type': 'bool'}},
                                                                                                  'type': 'list'},
                                                                                       'suppress': {'type': 'bool'}},
                                                                           'type': 'dict'}},
                                                     'type': 'dict'},
                                            'lower_layer_if': {'type': 'int'},
                                            'name': {'required': True, 'type': 'str'},
                                            'vlan_link_detect': {'type': 'bool'},
                                            'vrf': {'type': 'str'}},
                                'type': 'list'},
                     'state': {'choices': ['merged', 'replaced', 'overridden', 'deleted'],
                               'default': 'merged',
                               'type': 'str'}}  # pylint: disable=C0301
