#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from typing import Any, Mapping, Optional, Sequence

from cmk.base.check_api import passwordstore_get_cmdline
from cmk.base.config import special_agent_info


def agent_ucsbladecenter_arguments(
    params: Mapping[str, Any], hostname: str, ipaddress: Optional[str]
) -> Sequence[str | tuple[str, str, str]]:
    args = [
        "-u",
        f"{params['username']}",
        "-p",
        passwordstore_get_cmdline("%s", params["password"]),
    ]

    if params.get("no_cert_check"):
        args.append("--no-cert-check")

    args.append(ipaddress or hostname)
    return args


special_agent_info["ucs_bladecenter"] = agent_ucsbladecenter_arguments
