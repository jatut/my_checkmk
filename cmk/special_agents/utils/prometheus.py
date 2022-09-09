#!/usr/bin/env python3
# Copyright (C) 2021 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""
Common functions used in Prometheus related Special agents
"""

from cmk.utils import password_store

from cmk.special_agents.utils.request_helper import (
    create_api_connect_session,
    parse_api_custom_url,
    parse_api_url,
)


def extract_connection_args(config):
    connection_args = {
        "protocol": config.get("protocol"),
        "verify-cert": config.get("verify-cert", False),
    }

    if "auth_basic" in config:
        auth_info = config["auth_basic"][1]
        if config["auth_basic"][0] == "auth_login":
            connection_args.update(
                {
                    "auth": (
                        auth_info["username"],
                        password_store.extract(auth_info["password"]),
                    )
                }
            )
        else:
            connection_args.update({"token": password_store.extract(auth_info["token"])})

    connect_type, connect_settings = config["connection"]

    if connect_type == "url_custom":
        connection_args.update({"url_custom": connect_settings["url_address"]})
        return connection_args

    address = config["host_address"] if connect_type == "ip_address" else config["host_name"]

    path_prefix = connect_settings.get("path-prefix", "")
    if path_prefix:
        path_prefix = path_prefix + "/"

    connection_args.update(
        {"address": address, "path-prefix": path_prefix, "port": connect_settings.get("port")}
    )
    return connection_args


def generate_api_session(connection_options):
    if "url_custom" in connection_options:
        api_url = parse_api_custom_url(
            url_custom=connection_options["url_custom"],
            api_path="api/v1/",
            protocol=connection_options["protocol"],
        )
    else:
        api_url = parse_api_url(
            server_address=connection_options["address"],
            api_path=connection_options["path-prefix"] + "api/v1/",
            protocol=connection_options["protocol"],
            port=connection_options["port"],
        )
    return create_api_connect_session(
        api_url,
        auth=connection_options.get("auth"),
        token=connection_options.get("token"),
        no_cert_check=not connection_options["verify-cert"],
    )
