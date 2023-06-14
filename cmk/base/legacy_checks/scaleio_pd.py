#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.df import df_check_filesystem_list, FILESYSTEM_DEFAULT_PARAMS
from cmk.base.check_legacy_includes.scaleio import convert_scaleio_space
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable
from cmk.base.plugins.agent_based.utils.scaleio import parse_scaleio, ScaleioSection

# <<<scaleio_pd>>>
# PROTECTION_DOMAIN 91ebcf4500000000:
#        ID                                                 91ebcf4500000000
#        NAME                                               domain01
#        STATE                                              PROTECTION_DOMAIN_ACTIVE
#        MAX_CAPACITY_IN_KB                                 65.5 TB (67059 GB)
#        UNUSED_CAPACITY_IN_KB                              17.2 TB (17635 GB)


def parse_scaleio_pd(string_table: StringTable) -> ScaleioSection:
    return parse_scaleio(string_table, "PROTECTION_DOMAIN")


def inventory_scaleio_pd(parsed):
    for entry in parsed:
        yield entry, {}


def check_scaleio_pd(item, params, parsed):
    if not (data := parsed.get(item)):
        return

    # How will the data be represented? It's magic and the only
    # indication is the unit. We need to handle this!
    unit = data["MAX_CAPACITY_IN_KB"][3].strip(")")
    total = convert_scaleio_space(unit, int(data["MAX_CAPACITY_IN_KB"][2].strip("(")))
    free = convert_scaleio_space(unit, int(data["UNUSED_CAPACITY_IN_KB"][2].strip("(")))

    yield df_check_filesystem_list(item, params, [(item, total, free, 0)])


check_info["scaleio_pd"] = LegacyCheckDefinition(
    parse_function=parse_scaleio_pd,
    discovery_function=inventory_scaleio_pd,
    check_function=check_scaleio_pd,
    service_name="ScaleIO PD capacity %s",
    check_ruleset_name="filesystem",
    check_default_parameters=FILESYSTEM_DEFAULT_PARAMS,
)


def inventory_scaleio_pd_status(parsed):
    for entry in parsed:
        yield entry, None


def check_scaleio_pd_status(item, _no_params, parsed):
    if not (data := parsed.get(item)):
        return

    status = data["STATE"][0].replace("PROTECTION_DOMAIN_", "")
    state = 0 if status == "ACTIVE" else 2
    name = data["NAME"][0]

    yield state, "Name: %s, State: %s" % (name, status)


check_info["scaleio_pd.status"] = LegacyCheckDefinition(
    discovery_function=inventory_scaleio_pd_status,
    check_function=check_scaleio_pd_status,
    service_name="ScaleIO PD status %s",
)
