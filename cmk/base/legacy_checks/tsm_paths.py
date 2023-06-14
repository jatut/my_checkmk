#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info


def inventory_tsm_paths(info):
    return [(None, None)]


def check_tsm_paths(item, _no_params, info):
    count_pathes = len(info)
    error_paths = [x[1] for x in info if x[2] != "YES"]
    if len(error_paths) > 0:
        return 2, "Paths with errors: %s" % ", ".join(error_paths)
    return 0, " %d paths OK" % count_pathes


check_info["tsm_paths"] = LegacyCheckDefinition(
    check_function=check_tsm_paths,
    discovery_function=inventory_tsm_paths,
    service_name="TSM Paths",
)
