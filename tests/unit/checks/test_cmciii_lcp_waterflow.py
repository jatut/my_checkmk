#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Sequence

import pytest

from tests.testlib import Check

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable

pytestmark = pytest.mark.checks


@pytest.mark.parametrize(
    "string_table, discovered_item",
    [
        pytest.param(
            [
                [
                    "Waterflow",
                    "0.0 l/min",
                    "130.0 l/min",
                    "0.0 l/min",
                    "OK",
                    "2",
                    "Control-Valve",
                    "32 %",
                    "OK",
                    "2",
                    "Cooling-Capacity",
                    "0 W",
                    "OK",
                ],
            ],
            [(None, None)],
            id="Waterflow sensor is discovered within OID range.",
        ),
        pytest.param(
            [
                [
                    "Control-Valve",
                    "32 %",
                    "OK",
                    "2",
                    "Cooling-Capacity",
                    "0 W",
                    "OK",
                ],
            ],
            [(None, None)],
            id="Waterflow sensor is discovered even though there are no measurements for it.",
        ),
    ],
)
def test_discover_cmciii_lcp_waterflow(string_table: StringTable, discovered_item):
    check = Check("cmciii_lcp_waterflow")
    assert list(check.run_discovery(string_table)) == discovered_item


@pytest.mark.parametrize(
    "string_table, check_results",
    [
        pytest.param(
            [
                [
                    "Waterflow",
                    "0.0 l/min",
                    "130.0 l/min",
                    "0.0 l/min",
                    "OK",
                    "2",
                    "Control-Valve",
                    "32 %",
                    "OK",
                    "2",
                    "Cooling-Capacity",
                    "0 W",
                    "OK",
                ],
            ],
            [
                0,
                "Waterflow Status: OK Flow: 0.0, MinFlow: 0.0, MaxFLow: 130.0",
                [("flow", "0.0l/min", "0.0:130.0", 0, 0)],
            ],
            id="Check results of waterflow sensor measurements",
        ),
        pytest.param(
            [
                [
                    "Control-Valve",
                    "32 %",
                    "OK",
                    "2",
                    "Cooling-Capacity",
                    "0 W",
                    "OK",
                ],
            ],
            [3, "Waterflow information not found"],
            id="Check result when waterflow sensor measurements are missing.",
        ),
    ],
)
def test_check_cmciii_lcp_waterflow(string_table: StringTable, check_results: Sequence):
    check = Check("cmciii_lcp_waterflow")
    assert list(check.run_check("item not relevant", {}, string_table)) == check_results
