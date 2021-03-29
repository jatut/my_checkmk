#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest  # type: ignore[import]

from cmk.base.plugins.agent_based.cisco_asa_failover import (
    parse_cisco_asa_failover,
    discovery_cisco_asa_failover,
    check_cisco_asa_failover,
    Section,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Service


@pytest.mark.parametrize('string_table, expected', [
    pytest.param(
        [[['Failover LAN Interface', '2', 'ClusterLink Port-channel4 (system)'],
          ['Primary unit (this device)', '9', 'Active unit'], ['Secondary unit', '10', 'Standby unit'], ], ],
        Section(failover=True, local_role='primary', local_status='9', local_status_detail='Active unit',
                failver_link_status='2',
                remote_status='10'),
        id='Parse: Primary unit == Active unit'
    ),
    pytest.param(
        [[['Failover LAN Interface', '3', 'not Configured'], ['Primary unit (this device)', '3', 'Failover Off'],
          ['Secondary unit', '3', 'Failover Off'], ], ],
        Section(failover=False, local_role='primary', local_status='3', local_status_detail='Failover Off',
                failver_link_status='3', remote_status='3'),
        id='Parse: failover off/not configured'
    ),
])
def test_cisco_asa_failover_parse(string_table, expected):
    section = parse_cisco_asa_failover(string_table)
    assert section == expected


@pytest.mark.parametrize('section, expected', [
    pytest.param(
        Section(failover=True, local_role='primary', local_status='9', local_status_detail='Active unit',
                failver_link_status='2',
                remote_status='10'),
        [Service()],
        id='Discovery: Primary unit == Active unit',
    ),
    pytest.param(
        Section(failover=False, local_role='primary', local_status='3', local_status_detail='Failover Off',
                failver_link_status='3', remote_status='3'),
        [],
        id='Discovery: failover off/not configured',
    ),
])
def test_cisco_asa_failover_discover(section, expected):
    services = list(discovery_cisco_asa_failover(section))
    assert services == expected


@pytest.mark.parametrize('params, section, expected', [
    pytest.param(
        {'failover_state': 1, 'primary': 'active', 'secondary': 'standby'},
        Section(failover=True, local_role='primary', local_status='9', local_status_detail='Active unit',
                failver_link_status='2',
                remote_status='10'),
        [Result(state=State.OK, summary='Device (primary) is the Active unit'), ],
        id='Check: local unit == Primary unit == Active unit'
    ),
    pytest.param(
        {'failover_state': 1, 'primary': 'active', 'secondary': 'standby'},
        Section(failover=True, local_role='primary', local_status='10', local_status_detail='Standby unit',
                failver_link_status='2',
                remote_status='9'),
        [Result(state=State.OK, summary='Device (primary) is the Standby unit'),
         Result(state=State.WARN, summary='(The primary device should be active)')],
        id='Check: local unit == Primary unit == Standby unit'
    ),
    pytest.param(
        {'failover_state': 1, 'primary': 'active', 'secondary': 'standby'},
        Section(failover=True, local_role='primary', local_status='8', local_status_detail='Backup unit',
                failver_link_status='2',
                remote_status='10'),
        [Result(state=State.OK, summary='Device (primary) is the Backup unit'),
         Result(state=State.WARN, summary='(The primary device should be active)'),
         Result(state=State.WARN, summary='Unhandled state backup reported')],
        id='Check: local unit not active/standby'
    ),
    pytest.param(
        {'failover_state': 1, 'primary': 'active', 'secondary': 'standby'},
        Section(failover=True, local_role='primary', local_status='9', local_status_detail='Active unit',
                failver_link_status='3',
                remote_status='10'),
        [Result(state=State.OK, summary='Device (primary) is the Active unit'),
         Result(state=State.CRIT, summary='Failover link state is down'),
         ],
        id='Check: Failover link not up'
    ),
    pytest.param(
        {'failover_state': 1, 'primary': 'active', 'secondary': 'standby'},
        Section(failover=True, local_role='primary', local_status='9', local_status_detail='Active unit',
                failver_link_status='2',
                remote_status='8'),
        [Result(state=State.OK, summary='Device (primary) is the Active unit'),
         Result(state=State.WARN, summary='Unhandled state backup for remote device reported'),
         ],
        id='Check: Remote unit == not active/standby'
    ),
])
def test_cisco_asa_failover(params, section, expected):
    result = check_cisco_asa_failover(params, section)
    assert list(result) == expected
