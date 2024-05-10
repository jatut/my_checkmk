#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# <<<ad_replication>>>
# showrepl_COLUMNS,Destination DC Site,Destination DC,Naming Context,Source DC Site,Source DC,\
# Transport Type,Number of Failures,Last Failure Time,Last Success Time,Last Failure Status
# showrepl_INFO,Standardname-des-ersten-Standorts,WIN2003,"DC=corp,DC=de",Standardname-des-ers\
# ten-Standorts,WIN2003-DC2,RPC,0,0,2010-07-02 13:33:27,0
# showrepl_INFO,Standardname-des-ersten-Standorts,WIN2003,"CN=Configuration,DC=corp,DC=de",Sta\
# ndardname-des-ersten-Standorts,WIN2003-DC2,RPC,0,0,2010-07-02 12:54:08,0
# showrepl_INFO,Standardname-des-ersten-Standorts,WIN2003,"CN=Schema,CN=Configuration,DC=corp,\
# DC=de",Standardname-des-ersten-Standorts,WIN2003-DC2,RPC,0,0,2010-07-02 12:46:28,0


import time

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info

from cmk.agent_based.v2 import render, StringTable


def _get_relative_date_human_readable(timestamp: float) -> str:
    """Formats the given timestamp for humans "in ..." for future times
    or "... ago" for past timestamps."""
    seconds = timestamp - time.time()
    if seconds > 0:
        return "in " + render.timespan(seconds)
    return render.timespan(-seconds) + " ago"


def parse_ad_replication_dates(s):
    if s in {"0", "(never)"}:
        return None, "unknown"

    s_val = time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))
    return s_val, _get_relative_date_human_readable(s_val)


def parse_ad_replication_info(info):
    lines = []
    for line_parts in info:
        # Make lines split by , instead of spaces
        line_txt = " ".join(line_parts).replace(",CN=", ";CN=").replace(",DC=", ";DC=")
        line_parts = line_txt.split(",")
        if len(line_parts) in [11, 10]:
            lines.append(line_parts)
    return lines


def inventory_ad_replication(info):
    inv = []
    for line in parse_ad_replication_info(info):
        if len(line) == 11:
            source_site = line[4]
            source_dc = line[5]
        elif len(line) == 10:
            source_site = line[3]
            source_dc = line[4]
        else:
            break  # unhandled data
        entry = f"{source_site}/{source_dc}"
        if line[0] == "showrepl_INFO" and entry not in inv:
            inv.append(entry)
    yield from ((entry, {}) for entry in inv)


def check_ad_replication(item, params, info):
    status = 0
    long_output = []
    found_line = False
    count_failures = 0
    count_failed_repl = 0
    max_failures_warn, max_failures_crit = params["failure_levels"]

    for line in parse_ad_replication_info(info):
        if len(line) == 11:
            (
                line_type,
                _dest_site,
                _dest_dc,
                naming_context,
                source_site,
                source_dc,
                _transport,
                num_failures,
                time_last_failure,
                time_last_success,
                status_last_failure,
            ) = line
        elif len(line) == 10:
            (
                line_type,
                _dest_site,
                naming_context,
                source_site,
                source_dc,
                _transport,
                num_failures,
                time_last_failure,
                time_last_success,
                status_last_failure,
            ) = line
        else:
            continue  # unhandled data

        if line_type == "showrepl_INFO" and source_site + "/" + source_dc == item:
            found_line = True
            time_last_failure, time_last_failure_txt = parse_ad_replication_dates(time_last_failure)
            time_last_success, time_last_success_txt = parse_ad_replication_dates(time_last_success)

            failure_count = int(num_failures)

            if failure_count > max_failures_warn or failure_count > max_failures_crit:
                if failure_count > max_failures_crit:
                    status = 2
                    state_marker = "(!!)"
                else:
                    status = 1
                    state_marker = "(!)"

                count_failures += failure_count
                count_failed_repl += 1
                long_output.append(
                    "%s/%s replication of context %s reached "
                    " the threshold of maximum failures (%s) (Last success: %s, "
                    "Last failure: %s, Num failures: %s, Status: %s)%s"
                    % (
                        source_site,
                        source_dc,
                        naming_context,
                        max_failures_warn,
                        time_last_success_txt,
                        time_last_failure_txt,
                        num_failures,
                        status_last_failure,
                        state_marker,
                    )
                )

            if (
                time_last_failure is not None
                and time_last_success is not None
                and time_last_failure > time_last_success
            ):
                status = 2
                count_failures += 1
                count_failed_repl += 1
                long_output.append(
                    "%s/%s replication of context %s failed "
                    "(Last success: %s, Last failure: %s, Num failures: %s, Status: %s)(!!)"
                    % (
                        source_site,
                        source_dc,
                        naming_context,
                        time_last_success_txt,
                        time_last_failure_txt,
                        num_failures,
                        status_last_failure,
                    )
                )

    if not found_line:
        return

    if status == 0:
        yield 0, "All replications are OK."
        return

    yield status, (
        f"Replications with failures: {count_failed_repl}, Total failures: {count_failures}"
    )
    if long_output:
        yield 0, "\n%s" % "\n".join(long_output)
    return


def parse_ad_replication(string_table: StringTable) -> StringTable:
    return string_table


check_info["ad_replication"] = LegacyCheckDefinition(
    parse_function=parse_ad_replication,
    service_name="AD Replication %s",
    discovery_function=inventory_ad_replication,
    check_function=check_ad_replication,
    check_ruleset_name="ad_replication",
    check_default_parameters={
        "failure_levels": (15, 20),
    },
)
