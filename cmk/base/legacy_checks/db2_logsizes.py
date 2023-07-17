#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated"

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.db2 import parse_db2_dbs
from cmk.base.check_legacy_includes.df import df_check_filesystem_single
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import IgnoreResultsError

# <<<db2_logsizes>>>
# [[[db2taddm:CMDBS1]]]
# TIMESTAMP 1426495343
# usedspace 7250240
# logfilsiz 2048
# logprimary 6
# logsecond 100


def parse_db2_logsizes(string_table):
    pre_parsed = parse_db2_dbs(string_table)
    global_timestamp = pre_parsed[0]
    parsed = {}
    for key, values in pre_parsed[1].items():
        instance_info = {}
        for value in values:
            instance_info.setdefault(value[0], []).append(" ".join(map(str, (value[1:]))))
        # Some databases run in DPF mode. Means that the database is split over several nodes
        # Each node has its own logfile for the same database. We create one service for each logfile
        if "TIMESTAMP" not in instance_info:
            instance_info["TIMESTAMP"] = [global_timestamp]

        if "node" in instance_info:
            for node in instance_info["node"]:
                parsed["%s DPF %s" % (key, node)] = instance_info
        else:
            parsed[key] = instance_info

    return parsed


def inventory_db2_logsizes(parsed):
    for db, db_info in parsed.items():
        if "logfilsiz" in db_info:
            yield db, {}


def check_db2_logsizes(item, params, parsed):
    db = parsed.get(item)

    if not db:
        raise IgnoreResultsError("Login into database failed")

    # A DPF instance could look like
    # {'TIMESTAMP': ['1439976757'],
    #  u'logfilsiz': ['20480', '20480', '20480', '20480', '20480', '20480'],
    #  u'logprimary': ['13', '13', '13', '13', '13', '13'],
    #  u'logsecond': ['100', '100', '100', '100', '100', '100'],
    #  u'node': ['0 wasv091 0',
    #            '1 wasv091 1',
    #            '2 wasv091 2',
    #            '3 wasv091 3',
    #            '4 wasv091 4',
    #            '5 wasv091 5'],

    if "node" in db:
        node_key = " ".join(item.split()[2:])
        for idx, node in enumerate(db["node"]):
            if node == node_key:
                data_offset = idx
    else:
        data_offset = 0

    timestamp = int(db["TIMESTAMP"][0])

    if "logfilsiz" not in db:
        return 3, "Invalid database info"

    total = (
        int(db["logfilsiz"][data_offset])
        * (int(db["logprimary"][data_offset]) + int(db["logsecond"][data_offset]))
        * 4096
    )
    free = total - int(db["usedspace"][data_offset])

    return df_check_filesystem_single(
        item, total >> 20, free >> 20, 0, None, None, params, this_time=timestamp
    )


check_info["db2_logsizes"] = LegacyCheckDefinition(
    parse_function=parse_db2_logsizes,
    service_name="DB2 Logsize %s",
    discovery_function=inventory_db2_logsizes,
    check_function=check_db2_logsizes,
    check_ruleset_name="db2_logsize",
    check_default_parameters={
        "levels": (-20.0, -10.0),  # Interpreted as free space in df_check_filesystem_single
    },
)
