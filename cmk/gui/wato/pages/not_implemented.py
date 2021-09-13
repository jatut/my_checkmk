#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.globals import html
from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import mode_registry
from cmk.gui.plugins.wato.utils.base_modes import WatoMode


@mode_registry.register
class ModeNotImplemented(WatoMode):
    @classmethod
    def name(cls):
        return ""

    @classmethod
    def permissions(cls):
        return []

    def title(self):
        return _("Error")

    def page(self):
        html.show_error(_("This module has not yet been implemented."))
