#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info

sansymphony_alerts_default_values = (1, 2)


def inventory_sansymphony_alerts(info):
    return [(None, sansymphony_alerts_default_values)]


def check_sansymphony_alerts(_no_item, params, info):
    warn, crit = params
    nr_of_alerts = int(info[0][0])
    perfdata = [("alerts", nr_of_alerts, warn, crit)]
    infotxt = "Unacknowlegded alerts: %d" % nr_of_alerts
    levels = " (warn/crit at %d/%d)" % (warn, crit)

    state = 0
    if nr_of_alerts >= crit:
        state = 2
        infotxt += levels
    elif nr_of_alerts >= warn:
        state = 1
        infotxt += levels
    return state, infotxt, perfdata


check_info["sansymphony_alerts"] = LegacyCheckDefinition(
    check_function=check_sansymphony_alerts,
    discovery_function=inventory_sansymphony_alerts,
    service_name="sansymphony Alerts",
    check_ruleset_name="sansymphony_alerts",
)
