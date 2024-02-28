#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.plugins.elasticsearch.server_side_calls.special_agent import special_agent_elasticsearch
from cmk.server_side_calls.v1 import (
    HostConfig,
    IPAddressFamily,
    NetworkAddressConfig,
    PlainTextSecret,
    ResolvedIPAddressFamily,
)

TEST_HOST_CONFIG = HostConfig(
    name="my_host",
    resolved_ipv4_address="1.2.3.4",
    alias="my_alias",
    address_config=NetworkAddressConfig(
        ip_family=IPAddressFamily.IPV4,
    ),
    resolved_ip_family=ResolvedIPAddressFamily.IPV4,
)


def test_agent_elasticsearch_arguments_cert_check() -> None:
    params: dict[str, object] = {
        "hosts": ["testhost"],
        "protocol": "https",
        "infos": ["cluster_health", "nodestats", "stats"],
    }
    (cmd,) = special_agent_elasticsearch(params, TEST_HOST_CONFIG, {})
    assert "--no-cert-check" not in cmd.command_arguments

    params["no-cert-check"] = True
    (cmd,) = special_agent_elasticsearch(params, TEST_HOST_CONFIG, {})
    assert "--no-cert-check" in cmd.command_arguments


def test_agent_elasticsearch_arguments_password_store() -> None:
    params: dict[str, object] = {
        "hosts": ["testhost"],
        "protocol": "https",
        "infos": ["cluster_health", "nodestats", "stats"],
        "user": "user",
        "password": ("password", "pass"),
    }
    (cmd,) = special_agent_elasticsearch(params, TEST_HOST_CONFIG, {})
    assert cmd.command_arguments == [
        "-P",
        "https",
        "-m",
        "cluster_health",
        "nodestats",
        "stats",
        "-u",
        "user",
        "-s",
        PlainTextSecret(value="pass"),
        "testhost",
    ]
