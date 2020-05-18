#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author : thl-cmk[at]outlook[dot]com
# Date   : 2020-04-27
# Content: wato plugin for snmp check 'cisco_asa_vpnsessions'
#          to configure waring/critical levels
#
#
register_check_parameters(
    subgroup_applications,
    'cisco_asa_vpnsessions',
    _('Cisco VPN Sessions'),
    Dictionary(
        elements=[
            ('WarnCrit',
             Tuple(
                 title=_('Number of active sessions'),
                 help=_('This check monitors the number of active/peak sessions'),
                 elements=[
                     Integer(title=_('Warning at'), unit=_('sessions'), default_value=10),
                     Integer(title=_('Critical at'), unit=_('sessions'), default_value=100),
                 ],
             )
             )
        ]
    ),
    TextAscii(title=_('VPN Sessions')),
    match_type='dict',
)
