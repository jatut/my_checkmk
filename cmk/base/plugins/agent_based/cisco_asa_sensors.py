#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2021-03-18
#
# Monitor Cisco ASA temperature sensors
#
# 2021-02-25: rewrite for CMK 2.x
#
# sample snmpwalk
# .1.3.6.1.2.1.47.1.1.1.1.7.1 = STRING: "Chassis"
# .1.3.6.1.2.1.47.1.1.1.1.7.2 = STRING: "Processor 0/0"
# .1.3.6.1.2.1.47.1.1.1.1.7.3 = STRING: "Processor 0/1"
# .1.3.6.1.2.1.47.1.1.1.1.7.4 = STRING: "Processor 0/2"
# .1.3.6.1.2.1.47.1.1.1.1.7.5 = STRING: "ASA5515 Slot for Removable Drive 0"
# .1.3.6.1.2.1.47.1.1.1.1.7.6 = STRING: "Micron_M550_MTFDDAK128MAY Removable Drive in Slot 0"
# .1.3.6.1.2.1.47.1.1.1.1.7.7 = STRING: "Chassis Cooling Fan 1"
# .1.3.6.1.2.1.47.1.1.1.1.7.8 = STRING: "Chassis Fan Sensor 1"
# .1.3.6.1.2.1.47.1.1.1.1.7.9 = STRING: "Chassis Cooling Fan 2"
# .1.3.6.1.2.1.47.1.1.1.1.7.10 = STRING: "Chassis Fan Sensor 2"
# .1.3.6.1.2.1.47.1.1.1.1.7.11 = STRING: "Chassis Cooling Fan 3"
# .1.3.6.1.2.1.47.1.1.1.1.7.12 = STRING: "Chassis Fan Sensor 3"
# .1.3.6.1.2.1.47.1.1.1.1.7.13 = STRING: "CPU Temperature Sensor 0/0"
# .1.3.6.1.2.1.47.1.1.1.1.7.14 = STRING: "Chassis Ambient Temperature Sensor 1"
# .1.3.6.1.2.1.47.1.1.1.1.7.15 = STRING: "Chassis Ambient Temperature Sensor 2"
# .1.3.6.1.2.1.47.1.1.1.1.7.16 = STRING: "Chassis Ambient Temperature Sensor 3"
# .1.3.6.1.2.1.47.1.1.1.1.7.17 = STRING: "Gi0/0"
# .1.3.6.1.2.1.47.1.1.1.1.7.18 = STRING: "Gi0/1"
# .1.3.6.1.2.1.47.1.1.1.1.7.19 = STRING: "Gi0/2"
# .1.3.6.1.2.1.47.1.1.1.1.7.20 = STRING: "Gi0/3"
# .1.3.6.1.2.1.47.1.1.1.1.7.21 = STRING: "Gi0/4"
# .1.3.6.1.2.1.47.1.1.1.1.7.22 = STRING: "Gi0/5"
# .1.3.6.1.2.1.47.1.1.1.1.7.23 = STRING: "In0/0"
# .1.3.6.1.2.1.47.1.1.1.1.7.24 = STRING: "In0/1"
# .1.3.6.1.2.1.47.1.1.1.1.7.25 = STRING: "Ma0/0"
# .1.3.6.1.2.1.47.1.1.1.1.7.26 = STRING: "Po1"
#
# .1.3.6.1.2.1.99.1.1.1.1.8 = INTEGER: 10
# .1.3.6.1.2.1.99.1.1.1.1.10 = INTEGER: 10
# .1.3.6.1.2.1.99.1.1.1.1.12 = INTEGER: 10
# .1.3.6.1.2.1.99.1.1.1.1.13 = INTEGER: 8
# .1.3.6.1.2.1.99.1.1.1.1.14 = INTEGER: 8
# .1.3.6.1.2.1.99.1.1.1.1.15 = INTEGER: 8
# .1.3.6.1.2.1.99.1.1.1.1.16 = INTEGER: 8
# .1.3.6.1.2.1.99.1.1.1.4.8 = INTEGER: 7680
# .1.3.6.1.2.1.99.1.1.1.4.10 = INTEGER: 7936
# .1.3.6.1.2.1.99.1.1.1.4.12 = INTEGER: 7680
# .1.3.6.1.2.1.99.1.1.1.4.13 = INTEGER: 34
# .1.3.6.1.2.1.99.1.1.1.4.14 = INTEGER: 32
# .1.3.6.1.2.1.99.1.1.1.4.15 = INTEGER: 30
# .1.3.6.1.2.1.99.1.1.1.4.16 = INTEGER: 33
# .1.3.6.1.2.1.99.1.1.1.5.8 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.5.10 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.5.12 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.5.13 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.5.14 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.5.15 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.5.16 = INTEGER: 1
# .1.3.6.1.2.1.99.1.1.1.6.8 = STRING: "rpm"
# .1.3.6.1.2.1.99.1.1.1.6.10 = STRING: "rpm"
# .1.3.6.1.2.1.99.1.1.1.6.12 = STRING: "rpm"
# .1.3.6.1.2.1.99.1.1.1.6.13 = STRING: "celsius"
# .1.3.6.1.2.1.99.1.1.1.6.14 = STRING: "celsius"
# .1.3.6.1.2.1.99.1.1.1.6.15 = STRING: "celsius"
# .1.3.6.1.2.1.99.1.1.1.6.16 = STRING: "celsius"

#
# sample string_table
# [
#  [
#   ['Chassis', '', '', '', ''],
#   ['Processor 0/0', '', '', '', ''],
#   ['Processor 0/1', '', '', '', ''],
#   ['Processor 0/2', '', '', '', ''],
#   ['ASA5515 Slot for Removable Drive 0', '', '', '', ''],
#   ['Micron_M550_MTFDDAK128MAY Removable Drive in Slot 0', '', '', '', ''],
#   ['Chassis Cooling Fan 1', '', '', '', ''],
#   ['Chassis Fan Sensor 1', '10', '7680', '1', 'rpm'],
#   ['Chassis Cooling Fan 2', '', '', '', ''],
#   ['Chassis Fan Sensor 2', '10', '7936', '1', 'rpm'],
#   ['Chassis Cooling Fan 3', '', '', '', ''],
#   ['Chassis Fan Sensor 3', '10', '7680', '1', 'rpm'],
#   ['CPU Temperature Sensor 0/0', '8', '34', '1', 'celsius'],
#   ['Chassis Ambient Temperature Sensor 1', '8', '32', '1', 'celsius'],
#   ['Chassis Ambient Temperature Sensor 2', '8', '30', '1', 'celsius'],
#   ['Chassis Ambient Temperature Sensor 3', '8', '33', '1', 'celsius'],
#   ['Gi0/0', '', '', '', ''],
#   ['Gi0/1', '', '', '', ''],
#   ['Gi0/2', '', '', '', ''],
#   ['Gi0/3', '', '', '', ''],
#   ['Gi0/4', '', '', '', ''],
#   ['Gi0/5', '', '', '', ''],
#   ['In0/0', '', '', '', ''],
#   ['In0/1', '', '', '', ''],
#   ['Ma0/0', '', '', '', ''],
#   ['Po1', '', '', '', '']
#  ]
# ]
#
# sample section
# {'fan': {
#    'Chassis Sensor 1': CiscoAsaSensor(value=7680, status=<State.OK: 0>, state_readable='Ok', unit='rpm'),
#    'Chassis Sensor 2': CiscoAsaSensor(value=7936, status=<State.OK: 0>, state_readable='Ok', unit='rpm'),
#    'Chassis Sensor 3': CiscoAsaSensor(value=7680, status=<State.OK: 0>, state_readable='Ok', unit='rpm')
#   },
#  'temp': {
#    'CPU Sensor 0/0': CiscoAsaSensor(value=34.0, status=<State.OK: 0>, state_readable='Ok', unit='celsius'),
#    'Chassis Ambient Sensor 1': CiscoAsaSensor(value=32.0, status=<State.OK: 0>, state_readable='Ok', unit='celsius'),
#    'Chassis Ambient Sensor 2': CiscoAsaSensor(value=30.0, status=<State.OK: 0>, state_readable='Ok', unit='celsius'),
#    'Chassis Ambient Sensor 3': CiscoAsaSensor(value=33.0, status=<State.OK: 0>, state_readable='Ok', unit='celsius')
#   },
#  'power': {}}
#

from typing import Dict, List, NamedTuple

from .agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
    StringTable,
)

from .agent_based_api.v1 import (
    register,
    Service,
    Result,
    check_levels,
    State,
    SNMPTree,
    startswith,
)


# ##################################################################################################
#
# ASA TEMPERATURE BASE
#
# ##################################################################################################


class CiscoAsaSensor(NamedTuple):
    value: float
    status: State
    state_readable: str
    unit: str


def parse_cisco_asa_sensors(string_table: List[StringTable]) -> Dict:
    def get_state_readable(st: str) -> str:
        states = {
            '1': 'Ok',
            '2': 'unavailable',
            '3': 'nonoperational',
        }
        return states.get(st, st)

    def get_sensor_status(st: str) -> State:
        states = {
            '1': State.OK,
            '2': State.WARN,
            '3': State.CRIT
        }
        return states.get(st, State.CRIT)

    sensors: dict = {
        'fan': {},
        'temp': {},
        'power': {},
    }

    for sensorname, sensortype, sensorvalue, sensorstatus, sensorunits in string_table[0]:
        if sensorname != '':  # for asa context, there are no real sensors.
            if sensortype == '8':  # Temperature
                sensors['temp'].update({sensorname.replace('Temperature ', ''): CiscoAsaSensor(
                    value=to_celsius(float(sensorvalue), sensorunits),
                    unit=sensorunits,
                    status=get_sensor_status(sensorstatus),
                    state_readable=get_state_readable(sensorstatus),
                )})

            if sensortype == '10':  # Fan
                sensors['fan'].update({sensorname.replace('Fan ', ''): CiscoAsaSensor(
                    value=int(sensorvalue),
                    unit=sensorunits,
                    status=get_sensor_status(sensorstatus),
                    state_readable=get_state_readable(sensorstatus),
                )})

            if sensortype == '12':  # Power supply
                sensors['power'].update({sensorname.replace('Power ', ''): CiscoAsaSensor(
                    value=0,
                    unit='',
                    status=get_sensor_status(sensorstatus),
                    state_readable=get_state_readable(sensorstatus),
                )})

    return sensors


register.snmp_section(
    name='cisco_asa_sensors',
    parse_function=parse_cisco_asa_sensors,
    fetch=[
        SNMPTree(
            base='.1.3.6.1.2.1',  #
            oids=[
                '47.1.1.1.1.7',  # ENTITY-MIB::entPhysicalName
                '99.1.1.1.1',  # ENTITY-SENSOR-MIB::entPhySensorType
                '99.1.1.1.4',  # ENTITY-SENSOR-MIB::entPhySensorValue
                '99.1.1.1.5',  # ENTITY-SENSOR-MIB::entPhySensorOperStatus
                '99.1.1.1.6',  # ENTITY-SENSOR-MIB::entPhySensorUnitsDisplay
            ]
        ),
    ],
    detect=startswith('.1.3.6.1.2.1.1.1.0', 'cisco adaptive security appliance')
)

# ##################################################################################################
#
# ASA SENSORS TEMPERATURE
#
# ##################################################################################################

from .utils.temperature import (
    check_temperature,
    TempParamType,
    to_celsius,
)


def discovery_cisco_asa_temp(section: Dict) -> DiscoveryResult:
    for key in section['temp']:
        yield Service(item=key)


def check_cisco_asa_temp(item, params: TempParamType, section) -> CheckResult:
    try:
        sensor = section['temp'][item]

        yield Result(state=sensor.status, summary='Status: %s' % sensor.state_readable)

        yield from check_temperature(
            sensor.value,
            dev_unit=sensor.unit,
            dev_status=sensor.status,
            dev_status_name=sensor.state_readable,
            params=params,
            unique_name='check_cisco_asa_temp.%s' % item,
        )
    except KeyError:
        pass


register.check_plugin(
    name='cisco_asa_temp',
    service_name='Temperature %s',
    sections=['cisco_asa_sensors'],
    discovery_function=discovery_cisco_asa_temp,
    check_function=check_cisco_asa_temp,
    check_default_parameters={},
    check_ruleset_name='temperature'
)


# ##################################################################################################
#
# ASA SENSORS FAN
#
# ##################################################################################################

def render_rpm(value) -> str:
    return '%s RPM' % str(value)


def discovery_cisco_asa_fan(section: Dict) -> DiscoveryResult:
    for key in section['fan']:
        yield Service(item=key)


def check_cisco_asa_fan(item, params, section) -> CheckResult:
    try:
        sensor = section['fan'][item]

        yield Result(state=sensor.status, summary='Status: %s' % sensor.state_readable)

        yield from check_levels(
            sensor.value,
            label='Speed',
            levels_lower=params.get('levels_lower', None),
            levels_upper=params.get('levels_upper', None),
            metric_name='fan' if params.get('output_metrics') else None,
            render_func=render_rpm,
        )

    except KeyError:
        pass


register.check_plugin(
    name='cisco_asa_fan',
    service_name='Fan %s',
    sections=['cisco_asa_sensors'],
    discovery_function=discovery_cisco_asa_fan,
    check_function=check_cisco_asa_fan,
    check_default_parameters={'output_metrics': True},
    check_ruleset_name='hw_fans'
)


# ##################################################################################################
#
# ASA SENSORS POWER SUPPLY
#
# ##################################################################################################

def discovery_cisco_asa_power(section: Dict) -> DiscoveryResult:
    for key in section['power']:
        yield Service(item=key)


def check_cisco_asa_power(item, params, section) -> CheckResult:
    try:
        sensor = section['power'][item]

        yield Result(state=sensor.status, summary='Status: %s' % sensor.state_readable)

    except KeyError:
        pass


register.check_plugin(
    name='cisco_asa_power',
    service_name='Power %s',
    sections=['cisco_asa_sensors'],
    discovery_function=discovery_cisco_asa_power,
    check_function=check_cisco_asa_power,
    check_default_parameters={},
)
