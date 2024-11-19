#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.graphing.v1 import translations

translation_citrix_serverload = translations.Translation(
    name="citrix_serverload",
    check_commands=[translations.PassiveCheck("citrix_serverload")],
    translations={"perf": translations.RenameToAndScaleBy("citrix_load", 0.01)},
)

translation_genau_fan = translations.Translation(
    name="genau_fan",
    check_commands=[translations.PassiveCheck("genau_fan")],
    translations={"rpm": translations.RenameTo("fan")},
)

translation_ibm_svc_nodestats_disk_latency = translations.Translation(
    name="ibm_svc_nodestats_disk_latency",
    check_commands=[translations.PassiveCheck("ibm_svc_nodestats_disk_latency")],
    translations={
        "read_latency": translations.ScaleBy(0.001),
        "write_latency": translations.ScaleBy(0.001),
    },
)

# translation for lib function check_diskstat_dict
translation_disk_utilization_check_diskstat_dict = translations.Translation(
    name="disk_utilization_check_diskstat_dict",
    check_commands=[
        translations.PassiveCheck("diskstat_io"),
        translations.PassiveCheck("diskstat_io_director"),
        translations.PassiveCheck("diskstat_io_volumes"),
        translations.PassiveCheck("aws_ebs"),
        translations.PassiveCheck("aws_ec2_disk_io"),
        translations.PassiveCheck("aws_rds_disk_io"),
        translations.PassiveCheck("cadvisor_diskstat"),
        translations.PassiveCheck("scaleio_storage_pool_totalrw"),
        translations.PassiveCheck("scaleio_storage_pool_rebalancerw"),
        translations.PassiveCheck("scaleio_volume"),
        translations.PassiveCheck("ucd_diskio"),
        translations.PassiveCheck("winperf_phydisk"),
        translations.PassiveCheck("gcp_filestore_disk"),
        translations.PassiveCheck("gcp_sql_disk"),
        translations.PassiveCheck("esx_vsphere_counters_diskio"),
        translations.PassiveCheck("esx_vsphere_datastore_io"),
    ],
    translations={
        "disk_utilization": translations.ScaleBy(100.0),
    },
)
