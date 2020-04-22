#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the dmos facts module.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class FactsArgs(object):  # pylint: disable=R0903
    """ The arg spec for the dmos facts module
    """

    def __init__(self, **kwargs):
        pass

    choices = [
        'all',
        'log',
        'sntp',
        'vlan',
        'linkagg',
        'l2_interface',
        'lldp',
        'l3_interface',
        'user',
        'twamp',
    ]

    argument_spec = {
        'gather_subset': dict(default=['!config'], type='list'),
        'gather_network_resources': dict(choices=choices,
                                         type='list'),
    }
