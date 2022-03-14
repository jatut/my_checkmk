#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from ..agent_based_api.v1 import startswith

DETECT_2930M = startswith(".1.3.6.1.2.1.1.1.0", "Aruba 2930M")
