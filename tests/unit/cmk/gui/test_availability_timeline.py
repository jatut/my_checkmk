#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from tests.testlib import on_time

from cmk.gui.availability import (
    AVLayoutTimelineRow,
    AVObjectType,
    AVOptions,
    AVTimelineRows,
    AVTimelineSpan,
    AVTimelineStyle,
    layout_timeline,
)


@pytest.mark.parametrize(
    "what,timeline_rows,considered_duration,avoptions,style,expected",
    [
        pytest.param(
            "service",
            [
                (
                    {
                        "site": "stable",
                        "host_name": "stable",
                        "service_description": "CPU load",
                        "duration": 900,
                        "from": 1667381700,
                        "until": 1667382600,
                        "state": -1,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "",
                    },
                    "unmonitored",
                ),
                (
                    {
                        "site": "stable",
                        "host_name": "stable",
                        "service_description": "CPU load",
                        "duration": 900,
                        "from": 1667468100,
                        "until": 1667469000,
                        "state": 0,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "15 min load: 4.38, 15 min load per core: 0.55 (8 cores)",
                    },
                    "ok",
                ),
                (
                    {
                        "site": "stable",
                        "host_name": "stable",
                        "service_description": "CPU load",
                        "duration": 900,
                        "from": 1667554500,
                        "until": 1667555400,
                        "state": 0,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "15 min load: 4.38, 15 min load per core: 0.55 (8 cores)",
                    },
                    "ok",
                ),
            ],
            2700,
            {
                "range": ((1667379750, 1667566950), "The last 2 days 4 hours"),
                "rangespec": ("age", 187200),
                "labelling": [],
                "av_levels": None,
                "av_filter_outages": {"warn": 0.0, "crit": 0.0, "non-ok": 0.0},
                "outage_statistics": ([], []),
                "av_mode": False,
                "service_period": "honor",
                "notification_period": "ignore",
                "grouping": None,
                "dateformat": "yyyy-mm-dd hh:mm:ss",
                "timeformat": ("perc", "percentage_2", "seconds"),
                "short_intervals": 0,
                "dont_merge": False,
                "summary": "sum",
                "show_timeline": False,
                "timelimit": 30,
                "logrow_limit": 5000,
                "downtimes": {"include": "honor", "exclude_ok": False},
                "consider": {"flapping": True, "host_down": True, "unmonitored": True},
                "host_state_grouping": {"unreach": "unreach"},
                "state_grouping": {"warn": "warn", "unknown": "unknown", "host_down": "host_down"},
            },
            "standalone",
            [
                (None, "", 1.0416666666666667, "unmonitored"),
                (
                    0,
                    "From 2022-11-02 10:35:00 until 2022-11-02 10:50:00 (33.33%) During this time period no monitoring data is available",
                    0.9735576923076923,
                    "unmonitored",
                ),
                (None, "", 45.67307692307692, "unmonitored"),
                (
                    1,
                    "From 2022-11-03 10:35:00 until 2022-11-03 10:50:00 (33.33%) OK - 15 min load: 4.38, 15 min load per core: 0.55 (8 cores)",
                    0.9735576923076923,
                    "state0",
                ),
                (None, "", 45.67307692307692, "unmonitored"),
                (
                    2,
                    "From 2022-11-04 10:35:00 until 2022-11-04 10:50:00 (33.33%) OK - 15 min load: 4.38, 15 min load per core: 0.55 (8 cores)",
                    0.9735576923076923,
                    "state0",
                ),
                (None, "", 6.169871794871795, "unmonitored"),
            ],
            id="Timeline based on service times",
        ),
    ],
)
def test_layout_timeline_spans(
    what: AVObjectType,
    timeline_rows: AVTimelineRows,
    considered_duration: int,
    avoptions: AVOptions,
    style: AVTimelineStyle,
    expected: AVTimelineSpan,
) -> None:
    with on_time("2022-11-04 14:02:30,439", "CET"):
        assert (
            layout_timeline(
                what,
                timeline_rows,
                considered_duration,
                avoptions,
                style,
            )["spans"]
            == expected
        )


@pytest.mark.parametrize(
    "what,timeline_rows,considered_duration,avoptions,style,expected",
    [
        pytest.param(
            "service",
            [
                (
                    {
                        "site": "stable",
                        "host_name": "test",
                        "service_description": "Process test3",
                        "duration": 2950409,
                        "from": 1712042845,
                        "until": 1714993254,
                        "state": -1,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "No information about that period of time available",
                        "long_log_output": "",
                        "service_check_command": "check_mk-ps",
                        "service_custom_variables": {"ESCAPE_PLUGIN_OUTPUT": "0"},
                    },
                    "unmonitored",
                ),
                (
                    {
                        "site": "stable",
                        "host_name": "test",
                        "service_description": "Process test3",
                        "duration": 16,
                        "from": 1714993254,
                        "until": 1714993270,
                        "state": 2,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "Manually set to Critical by cmkadmin",
                        "long_log_output": "",
                        "service_check_command": "check_mk-ps",
                        "service_custom_variables": {"ESCAPE_PLUGIN_OUTPUT": "0"},
                    },
                    "crit",
                ),
                (
                    {
                        "site": "stable",
                        "host_name": "test",
                        "service_description": "Process test3",
                        "duration": 73575,
                        "from": 1714993270,
                        "until": 1715066845,
                        "state": 0,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "Processes: 7, Virtual memory: 13.0 MiB, Resident memory: 50.0 MiB, CPU: 0%, Process handles: 1054, Youngest running for: 11 days 12 hours, Oldest running for: 11 days 12 hours",
                        "long_log_output": "Processes: 7\nVirtual memory: 13.0 MiB\nResident memory: 50.0 MiB\nCPU: 0%\nProcess handles: 1054\nYoungest running for: 11 days 12 hours\nOldest running for: 11 days 12 hours\n<table><tr><th>name</th><th>user</th><th>virtual size</th><th>resident size</th><th>creation time</th><th>cpu usage (user space)</th><th>cpu usage (kernel space)</th><th>pid</th><th>cpu usage</th><th>pagefile usage</th><th>handle count</th></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.47 MiB</td><td>6.88 MiB</td><td>Apr 25 2024 00:22:34</td><td>0.0%</td><td>0.0%</td><td>3444</td><td>0.0%</td><td>1</td><td>166</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:36</td><td>0.0%</td><td>0.0%</td><td>6656</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.90 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6852</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.94 MiB</td><td>7.21 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6924</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.89 MiB</td><td>7.16 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6976</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>7132</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.89 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:38</td><td>0.0%</td",
                        "service_check_command": "check_mk-ps",
                        "service_custom_variables": {"ESCAPE_PLUGIN_OUTPUT": "0"},
                    },
                    "ok",
                ),
            ],
            3024000,
            {
                "range": ((1712042845, 1715066845), "The last 35 days"),
                "rangespec": 3024000,
                "labelling": ["timeline_long_output"],
                "av_levels": None,
                "av_filter_outages": {"warn": 0.0, "crit": 0.0, "non-ok": 0.0},
                "outage_statistics": ([], []),
                "av_mode": False,
                "service_period": "honor",
                "notification_period": "ignore",
                "grouping": None,
                "dateformat": "yyyy-mm-dd hh:mm:ss",
                "timeformat": ("perc", "percentage_2", "seconds"),
                "short_intervals": 0,
                "dont_merge": False,
                "summary": "sum",
                "show_timeline": False,
                "timelimit": 518430,
                "logrow_limit": 5000,
                "downtimes": {"include": "honor", "exclude_ok": False},
                "consider": {"flapping": True, "host_down": True, "unmonitored": True},
                "host_state_grouping": {"unreach": "unreach"},
                "state_grouping": {"warn": "warn", "unknown": "unknown", "host_down": "host_down"},
            },
            "standalone",
            [
                {
                    "state": "unmonitored",
                    "css": "unmonitored",
                    "state_name": "N/A",
                    "from": 1712042845,
                    "until": 1714993254,
                    "from_text": "2024-04-02 09:27:25",
                    "until_text": "2024-05-06 13:00:54",
                    "duration_text": "97.57%",
                    "log_output": "No information about that period of time available",
                },
                {
                    "state": "crit",
                    "css": "state2",
                    "state_name": "CRIT",
                    "from": 1714993254,
                    "until": 1714993270,
                    "from_text": "2024-05-06 13:00:54",
                    "until_text": "2024-05-06 13:01:10",
                    "duration_text": "0.00%",
                    "log_output": "Manually set to Critical by cmkadmin",
                },
                {
                    "state": "ok",
                    "css": "state0",
                    "state_name": "OK",
                    "from": 1714993270,
                    "until": 1715066845,
                    "from_text": "2024-05-06 13:01:10",
                    "until_text": "2024-05-07 09:27:25",
                    "duration_text": "2.43%",
                    "log_output": "Processes: 7, Virtual memory: 13.0 MiB, Resident memory: 50.0 MiB, CPU: 0%, Process handles: 1054, Youngest running for: 11 days 12 hours, Oldest running for: 11 days 12 hours",
                    "long_log_output": "Processes: 7\nVirtual memory: 13.0 MiB\nResident memory: 50.0 MiB\nCPU: 0%\nProcess handles: 1054\nYoungest running for: 11 days 12 hours\nOldest running for: 11 days 12 hours\n<table><tr><th>name</th><th>user</th><th>virtual size</th><th>resident size</th><th>creation time</th><th>cpu usage (user space)</th><th>cpu usage (kernel space)</th><th>pid</th><th>cpu usage</th><th>pagefile usage</th><th>handle count</th></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.47 MiB</td><td>6.88 MiB</td><td>Apr 25 2024 00:22:34</td><td>0.0%</td><td>0.0%</td><td>3444</td><td>0.0%</td><td>1</td><td>166</td></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:36</td><td>0.0%</td><td>0.0%</td><td>6656</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.90 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6852</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.94 MiB</td><td>7.21 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6924</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.89 MiB</td><td>7.16 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6976</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>7132</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:\\nginx-1.21.5\\nginx.exe</td><td>\\\\NT AUTHORITY\\SYSTEM</td><td>1.89 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:38</td><td>0.0%</td",
                },
            ],
            id="Escaped long output",
        ),
        pytest.param(
            "service",
            [
                (
                    {
                        "site": "stable",
                        "host_name": "test",
                        "service_description": "Process test3",
                        "duration": 2950409,
                        "from": 1712042845,
                        "until": 1714993254,
                        "state": -1,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "No information about that period of time available",
                        "long_log_output": "",
                        "service_check_command": "check_mk-ps",
                        "service_custom_variables": {"ESCAPE_PLUGIN_OUTPUT": "1"},
                    },
                    "unmonitored",
                ),
                (
                    {
                        "site": "stable",
                        "host_name": "test",
                        "service_description": "Process test3",
                        "duration": 16,
                        "from": 1714993254,
                        "until": 1714993270,
                        "state": 2,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "Manually set to Critical by cmkadmin",
                        "long_log_output": "",
                        "service_check_command": "check_mk-ps",
                        "service_custom_variables": {"ESCAPE_PLUGIN_OUTPUT": "1"},
                    },
                    "crit",
                ),
                (
                    {
                        "site": "stable",
                        "host_name": "test",
                        "service_description": "Process test3",
                        "duration": 73575,
                        "from": 1714993270,
                        "until": 1715066845,
                        "state": 0,
                        "host_down": 0,
                        "in_downtime": 0,
                        "in_host_downtime": 0,
                        "in_notification_period": 1,
                        "in_service_period": 1,
                        "is_flapping": 0,
                        "log_output": "Processes: 7, Virtual memory: 13.0 MiB, Resident memory: 50.0 MiB, CPU: 0%, Process handles: 1054, Youngest running for: 11 days 12 hours, Oldest running for: 11 days 12 hours",
                        "long_log_output": "Processes: 7\nVirtual memory: 13.0 MiB\nResident memory: 50.0 MiB\nCPU: 0%\nProcess handles: 1054\nYoungest running for: 11 days 12 hours\nOldest running for: 11 days 12 hours\n<table><tr><th>name</th><th>user</th><th>virtual size</th><th>resident size</th><th>creation time</th><th>cpu usage (user space)</th><th>cpu usage (kernel space)</th><th>pid</th><th>cpu usage</th><th>pagefile usage</th><th>handle count</th></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.47 MiB</td><td>6.88 MiB</td><td>Apr 25 2024 00:22:34</td><td>0.0%</td><td>0.0%</td><td>3444</td><td>0.0%</td><td>1</td><td>166</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:36</td><td>0.0%</td><td>0.0%</td><td>6656</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.90 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6852</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.94 MiB</td><td>7.21 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6924</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.89 MiB</td><td>7.16 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6976</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>7132</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.89 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:38</td><td>0.0%</td",
                        "service_check_command": "check_mk-ps",
                        "service_custom_variables": {"ESCAPE_PLUGIN_OUTPUT": "1"},
                    },
                    "ok",
                ),
            ],
            3024000,
            {
                "range": ((1712042845, 1715066845), "The last 35 days"),
                "rangespec": 3024000,
                "labelling": ["timeline_long_output"],
                "av_levels": None,
                "av_filter_outages": {"warn": 0.0, "crit": 0.0, "non-ok": 0.0},
                "outage_statistics": ([], []),
                "av_mode": False,
                "service_period": "honor",
                "notification_period": "ignore",
                "grouping": None,
                "dateformat": "yyyy-mm-dd hh:mm:ss",
                "timeformat": ("perc", "percentage_2", "seconds"),
                "short_intervals": 0,
                "dont_merge": False,
                "summary": "sum",
                "show_timeline": False,
                "timelimit": 518430,
                "logrow_limit": 5000,
                "downtimes": {"include": "honor", "exclude_ok": False},
                "consider": {"flapping": True, "host_down": True, "unmonitored": True},
                "host_state_grouping": {"unreach": "unreach"},
                "state_grouping": {"warn": "warn", "unknown": "unknown", "host_down": "host_down"},
            },
            "standalone",
            [
                {
                    "state": "unmonitored",
                    "css": "unmonitored",
                    "state_name": "N/A",
                    "from": 1712042845,
                    "until": 1714993254,
                    "from_text": "2024-04-02 09:27:25",
                    "until_text": "2024-05-06 13:00:54",
                    "duration_text": "97.57%",
                    "log_output": "No information about that period of time available",
                },
                {
                    "state": "crit",
                    "css": "state2",
                    "state_name": "CRIT",
                    "from": 1714993254,
                    "until": 1714993270,
                    "from_text": "2024-05-06 13:00:54",
                    "until_text": "2024-05-06 13:01:10",
                    "duration_text": "0.00%",
                    "log_output": "Manually set to Critical by cmkadmin",
                },
                {
                    "state": "ok",
                    "css": "state0",
                    "state_name": "OK",
                    "from": 1714993270,
                    "until": 1715066845,
                    "from_text": "2024-05-06 13:01:10",
                    "until_text": "2024-05-07 09:27:25",
                    "duration_text": "2.43%",
                    "log_output": "Processes: 7, Virtual memory: 13.0 MiB, Resident memory: 50.0 MiB, CPU: 0%, Process handles: 1054, Youngest running for: 11 days 12 hours, Oldest running for: 11 days 12 hours",
                    "long_log_output": "Processes: 7\nVirtual memory: 13.0 MiB\nResident memory: 50.0 MiB\nCPU: 0%\nProcess handles: 1054\nYoungest running for: 11 days 12 hours\nOldest running for: 11 days 12 hours\n<table><tr><th>name</th><th>user</th><th>virtual size</th><th>resident size</th><th>creation time</th><th>cpu usage (user space)</th><th>cpu usage (kernel space)</th><th>pid</th><th>cpu usage</th><th>pagefile usage</th><th>handle count</th></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.47 MiB</td><td>6.88 MiB</td><td>Apr 25 2024 00:22:34</td><td>0.0%</td><td>0.0%</td><td>3444</td><td>0.0%</td><td>1</td><td>166</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:36</td><td>0.0%</td><td>0.0%</td><td>6656</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.90 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6852</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.94 MiB</td><td>7.21 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6924</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.89 MiB</td><td>7.16 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>6976</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.93 MiB</td><td>7.19 MiB</td><td>Apr 25 2024 00:22:37</td><td>0.0%</td><td>0.0%</td><td>7132</td><td>0.0%</td><td>1</td><td>148</td></tr><tr><td>D:&bsol%3Bnginx-1.21.5&bsol%3Bnginx.exe</td><td>&bsol%3B&bsol%3BNT AUTHORITY&bsol%3BSYSTEM</td><td>1.89 MiB</td><td>7.17 MiB</td><td>Apr 25 2024 00:22:38</td><td>0.0%</td",
                },
            ],
            id="Unescaped long output",
        ),
    ],
)
def test_layout_timeline_table(
    what: AVObjectType,
    timeline_rows: AVTimelineRows,
    considered_duration: int,
    avoptions: AVOptions,
    style: AVTimelineStyle,
    expected: list[AVLayoutTimelineRow],
) -> None:
    with on_time("2024-07-05 09:27:25,968", "CET"):
        assert (
            layout_timeline(
                what,
                timeline_rows,
                considered_duration,
                avoptions,
                style,
            )["table"]
            == expected
        )
