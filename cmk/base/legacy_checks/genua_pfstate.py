#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.base.check_api import LegacyCheckDefinition, saveint
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

from cmk.plugins.lib.genua import DETECT_GENUA

# Example Agent Output:
# GENUA-MIB:
# .1.3.6.1.4.1.3717.2.1.1.6.1 = INTEGER: 300000
# .1.3.6.1.4.1.3717.2.1.1.6.2 = INTEGER: 1268
# .1.3.6.1.4.1.3717.2.1.1.6.3 = INTEGER: 1


genua_pfstate_default_levels = {"used": (None, None)}


def inventory_genua_pfstate(info):
    # remove empty elements due to alternative enterprise id in snmp_info
    info = [_f for _f in info if _f]

    if not info or not info[0]:
        return []

    if len(info[0][0]) == 3:
        return [(None, genua_pfstate_default_levels)]
    return []


def pfstate(st):
    names = {
        "0": "notOK",
        "1": "OK",
        "2": "unknown",
    }
    return names.get(st, st)


def check_genua_pfstate(item, params, info):
    # remove empty elements due to alternative enterprise id in snmp_info
    info = [_f for _f in info if _f]

    if info[0]:
        if len(info[0][0]) == 3:
            pfstateMax = saveint(info[0][0][0])
            pfstateUsed = saveint(info[0][0][1])
            pfstateStatus = info[0][0][2]
    else:
        return (3, "Invalid Output from Agent")

    warn, crit = params.get("used")
    if crit is None:
        crit = pfstateMax

    state = 0
    usedsym = ""
    statussym = ""
    if pfstateStatus != "1":
        state = 1
        statussym = "(!)"

    if crit and pfstateUsed > crit:
        state = 2
        usedsym = "(!!)"
    elif warn and pfstateUsed > warn:
        state = 1
        usedsym = "(!)"

    pfstatus = pfstate(str(pfstateStatus))
    infotext = "PF State: %s%s States used: %d%s States max: %d" % (
        pfstatus,
        statussym,
        pfstateUsed,
        usedsym,
        pfstateMax,
    )
    perfdata = [("statesused", pfstateUsed, None, pfstateMax)]
    return (state, infotext, perfdata)


check_info["genua_pfstate"] = LegacyCheckDefinition(
    detect=DETECT_GENUA,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.3717.2.1.1.6",
            oids=["1", "2", "3"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3137.2.1.1.6",
            oids=["1", "2", "3"],
        ),
    ],
    service_name="Paketfilter Status",
    discovery_function=inventory_genua_pfstate,
    check_function=check_genua_pfstate,
    check_ruleset_name="pf_used_states",
)
