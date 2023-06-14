#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# <<<citrix_serverload>>>
# 100


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info

citrix_serverload_default_levels = (8500, 9500)


def inventory_citrix_serverload(info):
    return [(None, citrix_serverload_default_levels)]


def check_citrix_serverload(_no_item, params, info):
    try:
        load = int(info[0][0])
    except Exception:
        yield 3, "Load information not found"
        return

    warn, crit = params
    state = 0
    if load == 20000:
        yield 1, "License error"
        load = 10000
    if load >= crit:
        state = 2
    elif load >= warn:
        state = 1
    yield state, "Current Citrix Load is: %.2f%%" % (load / 100.0), [("perf", load, warn, crit)]


check_info["citrix_serverload"] = LegacyCheckDefinition(
    check_ruleset_name="citrix_load",
    check_function=check_citrix_serverload,
    discovery_function=inventory_citrix_serverload,
    service_name="Citrix Serverload",
)
