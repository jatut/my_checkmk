#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Dict, Any  # pylint: disable=unused-import
import cmk.utils.paths
import cmk.utils.store as store

from cmk.gui.globals import g

GroupSpec = Dict[str, Any]  # TODO: Improve this type
GroupSpecs = Dict[str, GroupSpec]


def load_host_group_information():
    # type: () -> GroupSpecs
    return load_group_information()["host"]


def load_service_group_information():
    # type: () -> GroupSpecs
    return load_group_information()["service"]


def load_contact_group_information():
    # type: () -> GroupSpecs
    return load_group_information()["contact"]


def load_group_information():
    # type: () -> Dict[str, GroupSpecs]
    if "group_information" in g:
        return g.group_information

    cmk_base_groups = _load_cmk_base_groups()
    gui_groups = _load_gui_groups()

    # Merge information from Check_MK and Multisite worlds together
    groups = {}  # type: Dict[str, Dict[str, GroupSpec]]
    for what in ["host", "service", "contact"]:
        groups[what] = {}
        for gid, alias in cmk_base_groups['define_%sgroups' % what].items():
            groups[what][gid] = {'alias': alias}

            if gid in gui_groups['multisite_%sgroups' % what]:
                groups[what][gid].update(gui_groups['multisite_%sgroups' % what][gid])

    g.group_information = groups
    return groups


def _load_cmk_base_groups():
    """Load group information from Check_MK world"""
    group_specs = {
        "define_hostgroups": {},
        "define_servicegroups": {},
        "define_contactgroups": {},
    }  # type: Dict[str, GroupSpecs]

    return store.load_mk_file(cmk.utils.paths.check_mk_config_dir + "/wato/groups.mk",
                              default=group_specs)


def _load_gui_groups():
    # Now load information from the Web world
    group_specs = {
        "multisite_hostgroups": {},
        "multisite_servicegroups": {},
        "multisite_contactgroups": {},
    }  # type: Dict[str, GroupSpecs]

    return store.load_mk_file(cmk.utils.paths.default_config_dir + "/multisite.d/wato/groups.mk",
                              default=group_specs)
