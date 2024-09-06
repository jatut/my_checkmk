#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="arg-type"
import re
from collections.abc import Mapping, MutableSequence, Sequence
from typing import Literal, NamedTuple, TypedDict

from cmk.agent_based.v1.type_defs import StringTable
from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
)

FloatLevels = tuple[Literal["no_levels"], None] | tuple[Literal["fixed"], tuple[float, float]]


class Params(TypedDict):
    seconds_behind_master: FloatLevels | None


class Error(NamedTuple):
    message: str


Section = Error | dict[str, int | None | bool | Literal["NULL"]]


def _parse_mysql_slave(string_table: StringTable) -> Section:
    return (
        Error(" ".join(string_table[0]))
        if len(string_table) == 1
        and re.match(r"^ERROR [0-9 ()]+ at line \d+:", " ".join(string_table[0]))
        else {
            line[0][:-1]: (
                int(" ".join(line[1:]))
                if " ".join(line[1:]).isdigit()
                else {"Yes": True, "No": False, "None": None}.get(
                    " ".join(line[1:]), " ".join(line[1:])
                )
            )
            for line in string_table
            if line[0].endswith(":")
        }
    )


def parse_mysql_slave(
    string_table: StringTable,
) -> Mapping[str, Section]:
    grouped: dict[str, MutableSequence[Sequence[str]]] = {}
    item = "mysql"
    for line in string_table:
        if line[0].startswith("[["):
            item = " ".join(line).strip("[ ]") or item
            continue
        grouped.setdefault(item, []).append(line)
    return {k: _parse_mysql_slave(v) for k, v in grouped.items()}


agent_section_mysql_slave = AgentSection(
    name="mysql_slave",
    parse_function=parse_mysql_slave,
)


def discover_mysql_slave(
    section: Mapping[str, Section],
) -> DiscoveryResult:
    yield from (Service(item=item) for item, data in section.items() if data)


def check_mysql_slave(
    item: str,
    params: Params,
    section: Mapping[str, Section],
) -> CheckResult:
    if not (data := section.get(item)):
        return

    if isinstance(data, Error):
        yield Result(state=State.CRIT, summary=data.message)
        return

    if data["Slave_IO_Running"]:
        yield Result(state=State.OK, summary="Slave-IO: running")

        if rls := data["Relay_Log_Space"]:
            yield from check_levels(
                value=rls,
                metric_name="relay_log_space",
                label="Relay log",
                render_func=render.bytes,
            )

    else:
        yield Result(state=State.CRIT, summary="Slave-IO: not running")

    if not data["Slave_SQL_Running"]:
        yield Result(state=State.CRIT, summary="Slave-SQL: not running")
        return

    yield Result(state=State.OK, summary="Slave-SQL: running")

    # Makes only sense to monitor the age when the SQL slave is running
    if (sbm := data["Seconds_Behind_Master"]) == "NULL":
        yield Result(state=State.CRIT, summary="Time behind master: NULL (Lost connection?)")
        return

    yield from check_levels(
        value=sbm,
        metric_name="sync_latency",
        levels_upper=params.get("seconds_behind_master"),
        label="Time behind master",
        render_func=render.timespan,
    )


check_plugin_mysql_slave = CheckPlugin(
    name="mysql_slave",
    service_name="MySQL DB Slave %s",
    discovery_function=discover_mysql_slave,
    check_function=check_mysql_slave,
    check_ruleset_name="mysql_slave",
    check_default_parameters={
        "seconds_behind_master": None,
    },
)
