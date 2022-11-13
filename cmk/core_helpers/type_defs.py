#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Package containing the fetchers to the data sources."""

import enum
from collections.abc import Sequence
from typing import Final, NamedTuple

from cmk.utils.type_defs import HostAddress, HostName, SectionName, SourceType

__all__ = ["Mode", "NO_SELECTION", "SectionNameCollection", "SourceInfo", "FetcherType"]


class Mode(enum.Enum):
    NONE = enum.auto()
    CHECKING = enum.auto()
    DISCOVERY = enum.auto()
    INVENTORY = enum.auto()
    RTC = enum.auto()
    # Special case for discovery/checking/inventory command line argument where we specify in
    # advance all sections we want. Should disable caching, and in the SNMP case also detection.
    # Disabled sections must *not* be discarded in this mode.
    FORCE_SECTIONS = enum.auto()


class FetcherType(enum.Enum):
    """Map short name to fetcher class."""

    NONE = enum.auto()
    PUSH_AGENT = enum.auto()
    IPMI = enum.auto()
    PIGGYBACK = enum.auto()
    PROGRAM = enum.auto()
    SPECIAL_AGENT = enum.auto()
    SNMP = enum.auto()
    TCP = enum.auto()


class SourceInfo(NamedTuple):
    hostname: HostName
    ipaddress: HostAddress | None
    ident: str
    fetcher_type: FetcherType
    source_type: SourceType


# Note that the inner Sequence[str] to AgentRawDataSection
# is only **artificially** different from AgentRawData and
# obtained approximatively with `raw_data.decode("utf-8").split()`!
#
# Moreover, the type is not useful.
#
# What would be useful is a Mapping[SectionName, AgentRawData],
# analogous to SNMPRawData = Mapping[SectionName, SNMPRawDataSection],
# that would generalize to `Mapping[SectionName, TRawDataContent]` or
# `Mapping[SectionName, TRawData]` depending on which name we keep.
AgentRawDataSection = Sequence[str]


class SelectionType(enum.Enum):
    NONE = enum.auto()


SectionNameCollection = SelectionType | frozenset[SectionName]
# If preselected sections are given, we assume that we are interested in these
# and only these sections, so we may omit others and in the SNMP case
# must try to fetch them (regardles of detection).

NO_SELECTION: Final = SelectionType.NONE
