#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# fmt: off
# mypy: disable-error-code=var-annotated


checkname = "ibm_svc_portsas"


info = [
    [
        "0",
        "1",
        "6Gb",
        "1",
        "node1",
        "500507680305D3C0",
        "online",
        "",
        "host",
        "host_controller",
        "0",
        "1",
    ],
    [
        "1",
        "2",
        "6Gb",
        "1",
        "node1",
        "500507680309D3C0",
        "online",
        "",
        "host",
        "host_controller",
        "0",
        "2",
    ],
    [
        "2",
        "3",
        "6Gb",
        "1",
        "node1",
        "50050768030DD3C0",
        "online",
        "",
        "host",
        "host_controller",
        "0",
        "3",
    ],
    [
        "3",
        "4",
        "6Gb",
        "1",
        "node1",
        "500507680311D3C0",
        "offline",
        "500507680474F03F",
        "none",
        "enclosure",
        "0",
        "4",
    ],
    [
        "4",
        "5",
        "N/A",
        "1",
        "node1",
        "500507680315D3C0",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "1",
    ],
    [
        "5",
        "6",
        "N/A",
        "1",
        "node1",
        "500507680319D3C0",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "2",
    ],
    [
        "6",
        "7",
        "N/A",
        "1",
        "node1",
        "50050768031DD3C0",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "3",
    ],
    [
        "7",
        "8",
        "N/A",
        "1",
        "node1",
        "500507680321D3C0",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "4",
    ],
    [
        "8",
        "1",
        "6Gb",
        "2",
        "node2",
        "500507680305D3C1",
        "online",
        "",
        "host",
        "host_controller",
        "0",
        "1",
    ],
    [
        "9",
        "2",
        "6Gb",
        "2",
        "node2",
        "500507680309D3C1",
        "online",
        "",
        "host",
        "host_controller",
        "0",
        "2",
    ],
    [
        "10",
        "3",
        "6Gb",
        "2",
        "node2",
        "50050768030DD3C1",
        "online",
        "",
        "host",
        "host_controller",
        "0",
        "3",
    ],
    [
        "11",
        "4",
        "6Gb",
        "2",
        "node2",
        "500507680311D3C1",
        "offline",
        "500507680474F07F",
        "none",
        "enclosure",
        "0",
        "4",
    ],
    [
        "12",
        "5",
        "N/A",
        "2",
        "node2",
        "500507680315D3C1",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "1",
    ],
    [
        "13",
        "6",
        "N/A",
        "2",
        "node2",
        "500507680319D3C1",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "2",
    ],
    [
        "14",
        "7",
        "N/A",
        "2",
        "node2",
        "50050768031DD3C1",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "3",
    ],
    [
        "15",
        "8",
        "N/A",
        "2",
        "node2",
        "500507680321D3C1",
        "offline_unconfigured",
        "",
        "none",
        "host_controller",
        "1",
        "4",
    ],
]


discovery = {
    "": [
        ("Node 1 Slot 0 Port 1", {"current_state": "online"}),
        ("Node 1 Slot 0 Port 2", {"current_state": "online"}),
        ("Node 1 Slot 0 Port 3", {"current_state": "online"}),
        ("Node 1 Slot 0 Port 4", {"current_state": "offline"}),
        ("Node 2 Slot 0 Port 1", {"current_state": "online"}),
        ("Node 2 Slot 0 Port 2", {"current_state": "online"}),
        ("Node 2 Slot 0 Port 3", {"current_state": "online"}),
        ("Node 2 Slot 0 Port 4", {"current_state": "offline"}),
    ]
}


checks = {
    "": [
        (
            "Node 1 Slot 0 Port 1",
            {"current_state": "online"},
            [(0, "Status: online, Speed: 6Gb, Type: host_controller", [])],
        ),
        (
            "Node 1 Slot 0 Port 2",
            {"current_state": "online"},
            [(0, "Status: online, Speed: 6Gb, Type: host_controller", [])],
        ),
        (
            "Node 1 Slot 0 Port 3",
            {"current_state": "online"},
            [(0, "Status: online, Speed: 6Gb, Type: host_controller", [])],
        ),
        (
            "Node 1 Slot 0 Port 4",
            {"current_state": "offline"},
            [(0, "Status: offline, Speed: 6Gb, Type: enclosure", [])],
        ),
        (
            "Node 2 Slot 0 Port 1",
            {"current_state": "online"},
            [(0, "Status: online, Speed: 6Gb, Type: host_controller", [])],
        ),
        (
            "Node 2 Slot 0 Port 2",
            {"current_state": "online"},
            [(0, "Status: online, Speed: 6Gb, Type: host_controller", [])],
        ),
        (
            "Node 2 Slot 0 Port 3",
            {"current_state": "online"},
            [(0, "Status: online, Speed: 6Gb, Type: host_controller", [])],
        ),
        (
            "Node 2 Slot 0 Port 4",
            {"current_state": "offline"},
            [(0, "Status: offline, Speed: 6Gb, Type: enclosure", [])],
        ),
    ]
}
