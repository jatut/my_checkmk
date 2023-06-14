#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.mbg_lantime import (
    check_mbg_lantime_state_common,
    MBG_LANTIME_STATE_CHECK_DEFAULT_PARAMETERS,
)
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import all_of, equals, not_exists, SNMPTree


def inventory_mbg_lantime_state(info):
    if info:
        return [(None, {})]
    return []


def check_mbg_lantime_state(_no_item, params, info):
    states = {
        "0": (2, "not synchronized"),
        "1": (2, "no good reference clock"),
        "2": (0, "sync to external reference clock"),
        "3": (0, "sync to serial reference clock"),
        "4": (0, "normal operation PPS"),
        "5": (0, "normal operation reference clock"),
    }
    return check_mbg_lantime_state_common(states, _no_item, params, info)


check_info["mbg_lantime_state"] = LegacyCheckDefinition(
    detect=all_of(
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.5597.3"),
        not_exists(".1.3.6.1.4.1.5597.30.0.2.*"),
    ),
    check_function=check_mbg_lantime_state,
    discovery_function=inventory_mbg_lantime_state,
    service_name="LANTIME State",
    check_ruleset_name="mbg_lantime_state",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.5597.3.1",
        oids=["2", "3", "5", "7"],
    ),
    check_default_parameters=MBG_LANTIME_STATE_CHECK_DEFAULT_PARAMETERS,
)
