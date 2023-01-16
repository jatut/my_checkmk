#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# fmt: off
# type: ignore

from cmk.base.plugins.agent_based.esx_vsphere_hostsystem_section import parse_esx_vsphere_hostsystem

checkname = "esx_vsphere_hostsystem"

parsed = parse_esx_vsphere_hostsystem(
    [
        [
            "config.storageDevice.multipathInfo",
            "600143801259e9240000a00006460000",
            "fc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7f-naa.600143801259e9240000a00006460000",
            "active",
            "600143801259e9240000a00006460000",
            "fc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7b-naa.600143801259e9240000a00006460000",
            "active",
            "600143801259e9240000a00006460000",
            "fc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7a-naa.600143801259e9240000a00006460000",
            "active",
            "600143801259e9240000a00006460000",
            "fc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7e-naa.600143801259e9240000a00006460000",
            "active",
            "5001438024484b70",
            "fc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7f-naa.5001438024484b70",
            "active",
            "5001438024484b70",
            "fc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7b-naa.5001438024484b70",
            "active",
            "5001438024484b70",
            "fc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7a-naa.5001438024484b70",
            "active",
            "5001438024484b70",
            "fc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7e-naa.5001438024484b70",
            "active",
        ]
    ]
)

discovery = {
    "": [],
    "cpu_usage": [],
    "cpu_util_cluster": [],
    "maintenance": [],
    "mem_usage": [],
    "mem_usage_cluster": [],
    "multipath": [
        ("5001438024484b70", None),
        ("600143801259e9240000a00006460000", None),
    ],
    "state": [],
}

checks = {
    "multipath": [
        (
            "5001438024484b70",
            {},
            [
                (
                    0,
                    "4 active, 0 dead, 0 disabled, 0 standby, 0 unknown\nIncluded Paths:\nfc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7f-naa.5001438024484b70\nfc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7b-naa.5001438024484b70\nfc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7a-naa.5001438024484b70\nfc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7e-naa.5001438024484b70",
                    [],
                )
            ],
        ),
        (
            "600143801259e9240000a00006460000",
            {},
            [
                (
                    0,
                    "4 active, 0 dead, 0 disabled, 0 standby, 0 unknown\nIncluded Paths:\nfc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7f-naa.600143801259e9240000a00006460000\nfc.50060b0000c32e03:50060b0000c32e02-fc.5001438024484b70:5001438024484b7b-naa.600143801259e9240000a00006460000\nfc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7a-naa.600143801259e9240000a00006460000\nfc.50060b0000c32e01:50060b0000c32e00-fc.5001438024484b70:5001438024484b7e-naa.600143801259e9240000a00006460000",
                    [],
                )
            ],
        ),
    ]
}
