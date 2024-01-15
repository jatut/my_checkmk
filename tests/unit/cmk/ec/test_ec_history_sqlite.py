#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""EC History sqlite backend"""


import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from cmk.ec.history_sqlite import history_file_to_sqlite


@pytest.fixture(name="history_sqlite_raw")
def fixture_history_sqlite_raw() -> Iterator[sqlite3.Connection]:
    """history_sqlite_raw as an in :memory: database"""

    con = sqlite3.connect(":memory:")
    con.execute(
        """CREATE TABLE IF NOT EXISTS history
                             (time TEXT, what TEXT, who TEXT, addinfo TEXT, event_id INTEGER, count INTEGER, text TEXT, first FLOAT, last FLOAT,
                             comment TEXT, sl INTEGER, host TEXT, contact TEXT, application TEXT,
                             pid INTEGER, priority INTEGER, facility INTEGER, rule_id TEXT,
                             state INTEGER, phase TEXT, owner TEXT, match_groups TEXT,
                             contact_groups TEXT, ipaddress TEXT, orig_host TEXT,
                             contact_groups_precedence TEXT, core_host TEXT, host_in_downtime BOOL,
                             match_groups_syslog_application TEXT)"""
    )

    yield con

    con.execute("DROP TABLE IF EXISTS history")
    con.close()


def test_history_file_to_sqlite(tmp_path: Path, history_sqlite_raw: sqlite3.Connection) -> None:
    """History file saved correctly into sqlite inmemory DB."""

    path = tmp_path / "history_to_sqlite_test.log"
    path.write_text(
        """1666942211.07616	NEW			1002	1	some text	1666942208.0	1666942208.0		0	heute		OMD	0	6	9	asdf	0	open						host	heute	0	
1666942292.2998602	DELETE	cmkadmin		5	1	some text	1666942205.0	1666942205.0		0	heute		OMD	0	6	9	asdf	0	closed	cmkadmin					host	heute	0	
1666942292.2999856	DELETE	cmkadmin		6	1	some text	1666942205.0	1666942205.0		0	heute		OMD	0	6	9	asdf	0	closed	cmkadmin					host	heute	0	
1666942292.3000507	DELETE	cmkadmin		7	1	some text	1666942205.0	1666942205.0		0	heute		OMD	0	6	9	asdf	0	closed	cmkadmin					host	heute	0	"""
    )

    history_file_to_sqlite(path, history_sqlite_raw)

    cur = history_sqlite_raw.cursor()
    cur.execute("SELECT COUNT(*) FROM history;")
    assert cur.fetchone()[0] == 4


def test_history_file_to_sqlite_exceptions(
    tmp_path: Path, history_sqlite_raw: sqlite3.Connection
) -> None:
    """History file saved correctly into sqlite inmemory DB."""
    path = tmp_path / "history_to_sqlite_test.log"
    path.write_text("malformed file")

    with pytest.raises(sqlite3.ProgrammingError):
        history_file_to_sqlite(path, history_sqlite_raw)
