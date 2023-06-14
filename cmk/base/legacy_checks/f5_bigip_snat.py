#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated,arg-type"

import time

from cmk.base.check_api import (
    check_levels,
    get_bytes_human_readable,
    get_rate,
    LegacyCheckDefinition,
)
from cmk.base.check_legacy_includes.f5_bigip import DETECT
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree


def parse_f5_bigip_snat(info):
    snats = {}
    for line in info:
        name = line[0]
        snat_info = snats.setdefault(name, {})
        for index, stat in enumerate(
            (
                "if_in_pkts",
                "if_out_pkts",
                "if_in_octets",
                "if_out_octets",
                "connections_rate",
                "connections",
            ),
            start=1,
        ):
            try:
                stat_value = int(line[index])
            except ValueError:
                continue
            snat_info.setdefault(stat, []).append(stat_value)
    return {name: stats for name, stats in snats.items() if stats}


def inventory_f5_bigip_snat(parsed):
    for name in parsed:
        yield name, {}


def check_f5_bigip_snat(item, params, parsed):
    if item in parsed:
        snat = parsed[item]

        summed_values = {}
        now = time.time()
        # Calculate counters
        for what in [
            "if_in_pkts",
            "if_out_pkts",
            "if_in_octets",
            "if_out_octets",
            "connections_rate",
        ]:
            summed_values.setdefault(what, 0)
            if what not in snat:
                continue
            for idx, entry in enumerate(snat[what]):
                rate = get_rate("%s.%s" % (what, idx), now, entry)
                summed_values[what] += rate

        # Calculate sum value
        for what, function in [("connections", sum)]:
            summed_values[what] = function(snat[what])

        # Current number of connections
        yield (
            0,
            "Client connections: %d" % summed_values["connections"],
            list(summed_values.items()),
        )

        # New connections per time
        yield 0, "Rate: %.2f/sec" % summed_values["connections_rate"]

        # Check configured limits
        map_paramvar_to_text = {
            "if_in_octets": "Incoming Bytes",
            "if_out_octets": "Outgoing Bytes",
            "if_total_octets": "Total Bytes",
            "if_in_pkts": "Incoming Packets",
            "if_out_pkts": "Outgoing Packets",
            "if_total_pkts": "Total Packets",
        }
        summed_values["if_total_octets"] = (
            summed_values["if_in_octets"] + summed_values["if_out_octets"]
        )
        summed_values["if_total_pkts"] = summed_values["if_in_pkts"] + summed_values["if_out_pkts"]
        for param_var, levels in params.items():
            if param_var.endswith("_lower") and isinstance(levels, tuple):
                levels = (None, None) + levels
            value = summed_values[param_var.rstrip("_lower")]
            state, infotext, _extra_perfdata = check_levels(
                value,
                param_var,
                levels,
                human_readable_func=lambda x, p=param_var: get_bytes_human_readable(x, base=1000.0)
                if "octets" in p
                else str(x),
                infoname=map_paramvar_to_text[param_var.rstrip("_lower")],
            )
            if state:
                yield state, infotext


check_info["f5_bigip_snat"] = LegacyCheckDefinition(
    detect=DETECT,
    parse_function=parse_f5_bigip_snat,
    check_function=check_f5_bigip_snat,
    discovery_function=inventory_f5_bigip_snat,
    check_ruleset_name="f5_bigip_snat",
    service_name="Source NAT %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.3375.2.2.9.2.3.1",
        oids=["1", "2", "3", "4", "5", "7", "8"],
    ),
)
