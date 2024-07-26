#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# pylint: disable=consider-using-in

from .temperature import check_temperature

hp_proliant_status_map = {
    1: "unknown",
    2: "ok",
    3: "degraded",
    4: "failed",
    5: "disabled",
}

hp_proliant_status2nagios_map = {
    "unknown": 3,
    "other": 3,
    "ok": 0,
    "degraded": 2,
    "failed": 2,
    "disabled": 1,
}

hp_proliant_locale = {
    1: "other",
    2: "unknown",
    3: "system",
    4: "systemBoard",
    5: "ioBoard",
    6: "cpu",
    7: "memory",
    8: "storage",
    9: "removableMedia",
    10: "powerSupply",
    11: "ambient",
    12: "chassis",
    13: "bridgeCard",
    14: "managementBoard",
    15: "backplane",
    16: "networkSlot",
    17: "bladeSlot",
    18: "virtual",
}


def sanitize_item(item: str) -> str:
    r"""Sanitize null byte in item

    We observed some devices to send "\x00" (null-byte) as their name.
    Not all components delt well with it, so we replace it here
    with r"\x00" (literal backslash-x-zero-zero).
    As of Checkmk 2.3, this should in fact no longer be necessary.
    """
    return item.replace("\x00", r"\x00")


#   .--da cntlr------------------------------------------------------------.
#   |                     _                    _   _                       |
#   |                  __| | __ _    ___ _ __ | |_| |_ __                  |
#   |                 / _` |/ _` |  / __| '_ \| __| | '__|                 |
#   |                | (_| | (_| | | (__| | | | |_| | |                    |
#   |                 \__,_|\__,_|  \___|_| |_|\__|_|_|                    |
#   |                                                                      |
#   '----------------------------------------------------------------------'

hp_proliant_da_cntlr_cond_map = {
    "1": (3, "other"),
    "2": (0, "ok"),
    "3": (1, "degraded"),
    "4": (2, "failed"),
}

hp_proliant_da_cntlr_role_map = {
    "1": "other",
    "2": "notDuplexed",
    "3": "active",
    "4": "backup",
}

hp_proliant_da_cntlr_state_map = {
    "1": (3, "other"),
    "2": (0, "ok"),
    "3": (2, "general failure"),
    "4": (2, "cable problem"),
    "5": (2, "powered off"),
    "6": (1, "cache module missing"),
    "7": (2, "degraded"),
    "8": (0, "enabled"),
    "9": (0, "disabled"),
    "10": (1, "standby (offline)"),
    "11": (0, "standby (spare)"),
    "12": (1, "in test"),
    "13": (0, "starting"),
    "14": (2, "absent"),
    "16": (2, "unavailable (offline)"),
    "17": (0, "deferring"),
    "18": (0, "quiesced"),
    "19": (1, "updating"),
    "20": (0, "qualified"),
}


def inventory_hp_proliant_da_cntlr(info):
    if info:
        return [(line[0], None) for line in info]
    return []


def check_hp_proliant_da_cntlr(item, params, info):
    for line in info:
        index, model, slot, cond, role, b_status, b_cond, serial = line
        if index == item:
            sum_state = 0
            output = []

            for val, label, map_ in [
                (cond, "Condition", hp_proliant_da_cntlr_cond_map),
                (b_cond, "Board-Condition", hp_proliant_da_cntlr_cond_map),
                (b_status, "Board-Status", hp_proliant_da_cntlr_state_map),
            ]:
                this_state = map_[val][0]
                state_txt = ""
                if this_state == 1:
                    state_txt = " (!)"
                elif this_state == 2:
                    state_txt = " (!!)"
                sum_state = max(sum_state, this_state)
                output.append(f"{label}: {map_[val][1]}{state_txt}")

            output.append(
                "(Role: %s, Model: %s, Slot: %s, Serial: %s)"
                % (hp_proliant_da_cntlr_role_map.get(role, "unknown"), model, slot, serial)
            )

            return (sum_state, ", ".join(output))
    return (3, "Controller not found in snmp data")


# .
#   .--cpu-----------------------------------------------------------------.
#   |                                                                      |
#   |                           ___ _ __  _   _                            |
#   |                          / __| '_ \| | | |                           |
#   |                         | (__| |_) | |_| |                           |
#   |                          \___| .__/ \__,_|                           |
#   |                              |_|                                     |
#   '----------------------------------------------------------------------'

hp_proliant_cpu_status_map = {1: "unknown", 2: "ok", 3: "degraded", 4: "failed", 5: "disabled"}
hp_proliant_cpu_status2nagios_map = {
    "unknown": 3,
    "ok": 0,
    "degraded": 2,
    "failed": 2,
    "disabled": 1,
}


def inventory_hp_proliant_cpu(info):
    yield from ((sanitize_item(line[0]), {}) for line in info)


def check_hp_proliant_cpu(item, params, info):
    for line in info:
        if sanitize_item(line[0]) == item:
            index, slot, name, status = line
            snmp_status = hp_proliant_cpu_status_map[int(status)]
            status = hp_proliant_cpu_status2nagios_map[snmp_status]

            return (
                status,
                f'CPU{index} "{name}" in slot {slot} is in state "{snmp_status}"',
            )
    return (3, "item not found in snmp data")


# .
#   .--fans----------------------------------------------------------------.
#   |                          __                                          |
#   |                         / _| __ _ _ __  ___                          |
#   |                        | |_ / _` | '_ \/ __|                         |
#   |                        |  _| (_| | | | \__ \                         |
#   |                        |_|  \__,_|_| |_|___/                         |
#   |                                                                      |
#   '----------------------------------------------------------------------'

hp_proliant_fans_status_map = {1: "other", 2: "ok", 3: "degraded", 4: "failed"}
hp_proliant_speed_map = {1: "other", 2: "normal", 3: "high"}
hp_proliant_fans_locale = {
    1: "other",
    2: "unknown",
    3: "system",
    4: "systemBoard",
    5: "ioBoard",
    6: "cpu",
    7: "memory",
    8: "storage",
    9: "removableMedia",
    10: "powerSupply",
    11: "ambient",
    12: "chassis",
    13: "bridgeCard",
}


DISCLAIMER = (
    "HPE started to report the speed in percent without updating the MIB.\n"
    "This means that for a reported speed of 'other', 'normal' or 'high', "
    "there is the chance that the speed is actually 1, 2 or 3 percent respectively.\n"
    "This has no influence on the service state."
)


def inventory_hp_proliant_fans(info):
    for line in [l for l in info if l[2] == "3"]:
        label = hp_proliant_fans_locale.get(int(line[1]), "other")
        yield sanitize_item(f"{line[0]} ({label})"), {}


def _make_speed_label(speed: str) -> str:
    try:
        return "Speed is %s" % hp_proliant_speed_map[int(speed)]
    except KeyError:
        return "Speed is %s%%" % speed


def check_hp_proliant_fans(item, params, info):
    for line in info:
        label = "other"
        if len(line) > 1 and int(line[1]) in hp_proliant_fans_locale:
            label = hp_proliant_fans_locale[int(line[1])]

        if sanitize_item(f"{line[0]} ({label})") == item:
            index, _name, _present, speed, status, currentSpeed = line
            snmp_status = hp_proliant_fans_status_map[int(status)]
            status = hp_proliant_status2nagios_map[snmp_status]

            detailOutput = ""
            perfdata = []
            if currentSpeed != "":
                detailOutput = ", RPM: %s" % currentSpeed
                perfdata = [("temp", int(currentSpeed))]

            return (
                status,
                'FAN Sensor %s "%s", %s, State is %s%s\n%s'
                % (index, label, _make_speed_label(speed), snmp_status, detailOutput, DISCLAIMER),
                perfdata,
            )
    return (3, "item not found in snmp data")


# .
#   .--temperature---------------------------------------------------------.
#   |      _                                      _                        |
#   |     | |_ ___ _ __ ___  _ __   ___ _ __ __ _| |_ _   _ _ __ ___       |
#   |     | __/ _ \ '_ ` _ \| '_ \ / _ \ '__/ _` | __| | | | '__/ _ \      |
#   |     | ||  __/ | | | | | |_) |  __/ | | (_| | |_| |_| | | |  __/      |
#   |      \__\___|_| |_| |_| .__/ \___|_|  \__,_|\__|\__,_|_|  \___|      |
#   |                       |_|                                            |
#   '----------------------------------------------------------------------'


def format_hp_proliant_name(line):
    return f"{line[0]} ({hp_proliant_locale[int(line[1])]})"


def inventory_hp_proliant_temp(info):
    for line in info:
        if line[-1] != "1":
            # other(1): Temperature could not be determined
            yield format_hp_proliant_name(line), {}


def check_hp_proliant_temp(item, params, info):
    for line in info:
        if format_hp_proliant_name(line) == item:
            value, threshold, status = line[2:]

            # This case means no threshold available and
            # the devices' web interface displays "N/A"
            if threshold == "-99" or threshold == "0":
                devlevels = None
            else:
                threshold = float(threshold)
                devlevels = (threshold, threshold)

            snmp_status = hp_proliant_status_map[int(status)]

            return check_temperature(
                float(value),
                params,
                "hp_proliant_temp_%s" % item,
                dev_levels=devlevels,
                dev_status=hp_proliant_status2nagios_map[snmp_status],
                dev_status_name="Unit: %s" % snmp_status,
            )
    return 3, "item not found in snmp data"


# .
#   .--scan function-------------------------------------------------------.
#   |                           __                  _   _                  |
#   |    ___  ___ __ _ _ __    / _|_   _ _ __   ___| |_(_) ___  _ __       |
#   |   / __|/ __/ _` | '_ \  | |_| | | | '_ \ / __| __| |/ _ \| '_ \      |
#   |   \__ \ (_| (_| | | | | |  _| |_| | | | | (__| |_| | (_) | | | |     |
#   |   |___/\___\__,_|_| |_| |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|     |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'


def hp_proliant_scan_function(oid):
    # migrated!
    return (
        "proliant" in oid(".1.3.6.1.4.1.232.2.2.4.2.0", "").lower()
        or "storeeasy" in oid(".1.3.6.1.4.1.232.2.2.4.2.0", "").lower()
        or "synergy" in oid(".1.3.6.1.4.1.232.2.2.4.2.0", "").lower()
    )


# .
