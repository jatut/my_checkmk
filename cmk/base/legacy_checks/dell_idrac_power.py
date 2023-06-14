#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# example output


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree, startswith


def inventory_dell_idrac_power(info):
    for index, _status, _count in info[0]:
        yield index, None


def check_dell_idrac_power(item, _no_params, info):
    translate_status = {
        "1": (3, "other"),
        "2": (3, "unknown"),
        "3": (0, "full"),
        "4": (1, "degraded"),
        "5": (2, "lost"),
        "6": (0, "not redundant"),
        "7": (1, "redundancy offline"),
    }

    for index, status, _count in info[0]:
        if index == item:
            state, state_readable = translate_status[status]
            yield state, "Status: %s" % state_readable


check_info["dell_idrac_power"] = LegacyCheckDefinition(
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.674.10892.5"),
    discovery_function=inventory_dell_idrac_power,
    check_function=check_dell_idrac_power,
    service_name="Power Supply Redundancy %s",
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.674.10892.5.4.600.10.1",
            oids=["2", "5", "6"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.674.10892.5.4.600.12.1",
            oids=["2", "5", "7", "8"],
        ),
    ],
)


def inventory_dell_idrac_power_unit(info):
    for index, _status, _psu_type, _location in info[1]:
        yield index, None


def check_dell_idrac_power_unit(item, _no_params, info):
    translate_status = {
        "1": (3, "OTHER"),
        "2": (3, "UNKNOWN"),
        "3": (0, "OK"),
        "4": (1, "NONCRITICAL"),
        "5": (2, "CRITICAL"),
        "6": (2, "NONRECOVERABLE"),
    }

    translate_type = {
        "1": "OTHER",
        "2": "UNKNOWN",
        "3": "LINEAR",
        "4": "SWITCHING",
        "5": "BATTERY",
        "6": "UPS",
        "7": "CONVERTER",
        "8": "REGULATOR",
        "9": "AC",
        "10": "DC",
        "11": "VRM",
    }

    for index, status, psu_type, location in info[1]:
        if index == item:
            state, state_readable = translate_status[status]
            psu_type_readable = translate_type[psu_type]
            yield state, "Status: %s, Type: %s, Name: %s" % (
                state_readable,
                psu_type_readable,
                location,
            )


check_info["dell_idrac_power.unit"] = LegacyCheckDefinition(
    discovery_function=inventory_dell_idrac_power_unit,
    check_function=check_dell_idrac_power_unit,
    service_name="Power Supply %s",
)
