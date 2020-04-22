#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The facts class for dmos
this file validates each subset of facts and selectively
calls the appropriate facts gathering function
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.argspec.facts.facts import FactsArgs
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.log.log import LogFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.sntp.sntp import SntpFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.vlan.vlan import VlanFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.linkagg.linkagg import LinkaggFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.l2_interface.l2_interface import L2_interfaceFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.lldp.lldp import LldpFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.l3_interface.l3_interface import L3_interfaceFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.user.user import UserFacts
from ansible_collections.datacom.dmos.plugins.module_utils.network.dmos.facts.twamp.twamp import TwampFacts


FACT_LEGACY_SUBSETS = {}
FACT_RESOURCE_SUBSETS = dict(
    log=LogFacts,
    sntp=SntpFacts,
    vlan=VlanFacts,
    linkagg=LinkaggFacts,
    l2_interface=L2_interfaceFacts,
    lldp=LldpFacts,
    l3_interface=L3_interfaceFacts,
    user=UserFacts,
    twamp=TwampFacts,
)



class Facts(FactsBase):
    """ The fact class for dmos
    """

    VALID_LEGACY_GATHER_SUBSETS = frozenset(FACT_LEGACY_SUBSETS.keys())
    VALID_RESOURCE_SUBSETS = frozenset(FACT_RESOURCE_SUBSETS.keys())

    def __init__(self, module):
        super(Facts, self).__init__(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        """ Collect the facts for dmos

        :param legacy_facts_type: List of legacy facts types
        :param resource_facts_type: List of resource fact types
        :param data: previously collected conf
        :rtype: dict
        :return: the facts gathered
        """
        if self.VALID_RESOURCE_SUBSETS:
            self.get_network_resources_facts(FACT_RESOURCE_SUBSETS, resource_facts_type, data)

        if self.VALID_LEGACY_GATHER_SUBSETS:
            self.get_network_legacy_facts(FACT_LEGACY_SUBSETS, legacy_facts_type)

        return self.ansible_facts, self._warnings
