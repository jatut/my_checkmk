#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from typing import Optional

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Metric, Result, Service, State
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)
from cmk.base.plugins.agent_based.aws_lambda_performance import (
    _DEFAULT_PARAMETERS,
    _MORE_THAN_ONE_PER_HOUR,
    check_aws_lambda_performance,
    discover_aws_lambda,
    LambdaCloudwatchMetrics,
    LambdaCloudwatchSection,
    LambdaPerformanceParameters,
    LambdaSummarySection,
    parse_aws_lambda,
)
from cmk.base.plugins.agent_based.utils.aws import CloudwatchInsightsSection

from .utils.test_aws import SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS, SECTION_AWS_LAMBDA_SUMMARY

# this is the metric data when a lambda function is not used in the last monitoring interval
_STRING_TABLE_AWS_LAMBDA_NOT_USED = [
    [
        '[{"Id":',
        '"id_0_ConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DeadLetterErrors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DestinationDeliveryFailures",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Duration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Errors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Invocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_IteratorAge",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_PostRuntimeExtensionsDuration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencySpilloverInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyUtilization",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Throttles",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_UnreservedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"}]',
    ],
    [
        '[{"Id":',
        '"id_0_ConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DeadLetterErrors",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DestinationDeliveryFailures",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Duration",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Errors",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Invocations",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_IteratorAge",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_PostRuntimeExtensionsDuration",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencySpilloverInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyUtilization",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Throttles",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_UnreservedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"}]',
    ],
]

# this is the metric data for three invocations of my_python_test_function
_STRING_TABLE_AWS_LAMBDA = [
    [
        '[{"Id":',
        '"id_0_ConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DeadLetterErrors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DestinationDeliveryFailures",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Duration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[902.3766666666667, null]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Errors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Invocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[3.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_IteratorAge",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_PostRuntimeExtensionsDuration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencySpilloverInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyUtilization",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Throttles",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_UnreservedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"}]',
    ],
    [
        '[{"Id":',
        '"id_0_ConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DeadLetterErrors",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DestinationDeliveryFailures",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Duration",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Errors",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Invocations",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_IteratorAge",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_PostRuntimeExtensionsDuration",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencySpilloverInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyUtilization",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Throttles",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_UnreservedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-north-1:710145618630:function:myLambdaTestFunction",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"}]',
    ],
]

# this is the artificial metric data for possible misbehaviour of AWS lambda or the agent (duration is zero)
_STRING_TABLE_AWS_LAMBDA_INVALID_DATA = [
    [
        '[{"Id":',
        '"id_0_ConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DeadLetterErrors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DestinationDeliveryFailures",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Duration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, null]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Errors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Invocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_IteratorAge",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_PostRuntimeExtensionsDuration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencySpilloverInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyUtilization",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Throttles",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_UnreservedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"}]',
    ],
]

# this is the artificial metric data for missing metrics. This would be an error of AWS lambda or the agent
_STRING_TABLE_AWS_LAMBDA_MISSING_MANDATORY_METRIC = [
    [
        '[{"Id":',
        '"id_0_ConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DeadLetterErrors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_DestinationDeliveryFailures",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        # metric for duration is missing
        '{"Id":',
        '"id_0_Errors",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Invocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_IteratorAge",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_PostRuntimeExtensionsDuration",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencySpilloverInvocations",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrencyUtilization",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_ProvisionedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_Throttles",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        '["2021-07-08 10:55:00+00:00"],',
        '"Values":',
        "[[0.0, 600]],",
        '"StatusCode":',
        '"Complete"},',
        '{"Id":',
        '"id_0_UnreservedConcurrentExecutions",',
        '"Label":',
        '"arn:aws:lambda:eu-central-1:710145618630:function:my_python_test_function",',
        '"Timestamps":',
        "[],",
        '"Values":',
        "[],",
        '"StatusCode":',
        '"Complete"}]',
    ],
]

_SECTION_AWS_LAMBDA: LambdaCloudwatchSection = {
    "eu-central-1 my_python_test_function": LambdaCloudwatchMetrics(
        Duration=902.3766666666667,
        Errors=0.0,
        Invocations=0.005,
        Throttles=0.0,
        ConcurrentExecutions=None,
        DeadLetterErrors=None,
        DestinationDeliveryFailures=None,
        IteratorAge=None,
        PostRuntimeExtensionsDuration=None,
        ProvisionedConcurrencyInvocations=None,
        ProvisionedConcurrencySpilloverInvocations=None,
        ProvisionedConcurrencyUtilization=None,
        ProvisionedConcurrentExecutions=None,
        UnreservedConcurrentExecutions=None,
    )
}

_SECTION_AWS_LAMBDA_INVALID_DATA: LambdaCloudwatchSection = {
    "eu-central-1 my_python_test_function": LambdaCloudwatchMetrics(
        Duration=0.0,
        Errors=0.0,
        Invocations=0.0,
        Throttles=0.0,
        ConcurrentExecutions=None,
        DeadLetterErrors=None,
        DestinationDeliveryFailures=None,
        IteratorAge=None,
        PostRuntimeExtensionsDuration=None,
        ProvisionedConcurrencyInvocations=None,
        ProvisionedConcurrencySpilloverInvocations=None,
        ProvisionedConcurrencyUtilization=None,
        ProvisionedConcurrentExecutions=None,
        UnreservedConcurrentExecutions=None,
    )
}


@pytest.mark.parametrize(
    "string_table_aws_lambda, results",
    [
        (_STRING_TABLE_AWS_LAMBDA_NOT_USED, {}),
        (_STRING_TABLE_AWS_LAMBDA, _SECTION_AWS_LAMBDA),
        (_STRING_TABLE_AWS_LAMBDA_INVALID_DATA, _SECTION_AWS_LAMBDA_INVALID_DATA),
    ],
)
def test_parse_aws_lambda(
    string_table_aws_lambda: StringTable, results: Optional[LambdaCloudwatchSection]
) -> None:
    assert parse_aws_lambda(string_table_aws_lambda) == results


@pytest.mark.parametrize(
    "string_table_aws_lambda, results",
    [
        (
            _STRING_TABLE_AWS_LAMBDA_MISSING_MANDATORY_METRIC,
            None,
        ),
    ],
)
def test_parse_aws_lambda_missing_mandatory_metric(
    string_table_aws_lambda: StringTable, results: Optional[LambdaCloudwatchSection]
) -> None:
    with pytest.raises(TypeError):
        assert parse_aws_lambda(string_table_aws_lambda) == results


_PARAMETER_DURATION_ABSOLUTE: LambdaPerformanceParameters = _DEFAULT_PARAMETERS.copy()
_PARAMETER_DURATION_ABSOLUTE["levels_duration_absolute"] = (5.0, 10.0)


@pytest.mark.parametrize(
    "item, params, section_aws_lambda_summary, section_aws_lambda, section_aws_lambda_cloudwatch_insights, results",
    [
        (
            "eu-central-1 my_python_test_function",
            _DEFAULT_PARAMETERS,
            SECTION_AWS_LAMBDA_SUMMARY,
            None,
            SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS,
            [
                Result(state=State.OK, summary="Invocations: 0.0000/s"),
                Metric("aws_lambda_invocations", 0.0),
            ],
        ),
        (
            "eu-central-1 my_python_test_function",
            _DEFAULT_PARAMETERS,
            SECTION_AWS_LAMBDA_SUMMARY,
            _SECTION_AWS_LAMBDA,
            SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS,
            [
                Result(
                    state=State.WARN,
                    summary='Duration in percent of AWS Lambda "timeout" limit: 90.24% (warn/crit at 90.00%/95.00%)',
                ),
                Metric("aws_lambda_duration_in_percent", 90.23766666666667, levels=(90.0, 95.0)),
                Result(state=State.OK, summary="Errors: 0.0000/s"),
                Metric("error_rate", 0.0, levels=(0.00028, 0.00028)),
                Result(state=State.OK, summary="Invocations: 0.0050/s"),
                Metric("aws_lambda_invocations", 0.005),
                Result(state=State.OK, summary="Throttles: 0.0000/s"),
                Metric("aws_lambda_throttles", 0.0, levels=(0.00028, 0.00028)),
                Result(state=State.OK, summary="Init duration with absolute limits: 2 seconds"),
                Metric("aws_lambda_init_duration_absolute", 1.62853),
                Result(
                    state=State.CRIT,
                    summary="Cold starts in percent: 50.00% (warn/crit at 10.00%/20.00%)",
                ),
                Metric("aws_lambda_cold_starts_in_percent", 50.0, levels=(10.0, 20.0)),
            ],
        ),
        (
            "eu-central-1 my_python_test_function",
            _DEFAULT_PARAMETERS,
            SECTION_AWS_LAMBDA_SUMMARY,
            _SECTION_AWS_LAMBDA_INVALID_DATA,
            SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS,
            [
                Result(
                    state=State.OK, summary='Duration in percent of AWS Lambda "timeout" limit: 0%'
                ),
                Metric("aws_lambda_duration_in_percent", 0.0, levels=(90.0, 95.0)),
                Result(state=State.OK, summary="Errors: 0.0000/s"),
                Metric("error_rate", 0.0, levels=(0.00028, 0.00028)),
                Result(state=State.OK, summary="Invocations: 0.0000/s"),
                Metric("aws_lambda_invocations", 0.000),
                Result(state=State.OK, summary="Throttles: 0.0000/s"),
                Metric("aws_lambda_throttles", 0.0, levels=(0.00028, 0.00028)),
                Result(state=State.OK, summary="Init duration with absolute limits: 2 seconds"),
                Metric("aws_lambda_init_duration_absolute", 1.62853),
                Result(
                    state=State.CRIT,
                    summary="Cold starts in percent: 50.00% (warn/crit at 10.00%/20.00%)",
                ),
                Metric("aws_lambda_cold_starts_in_percent", 50.0, levels=(10.0, 20.0)),
            ],
        ),
        (
            "eu-central-1 my_python_test_function",
            _PARAMETER_DURATION_ABSOLUTE,
            SECTION_AWS_LAMBDA_SUMMARY,
            _SECTION_AWS_LAMBDA,
            SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS,
            [
                Result(
                    state=State.WARN,
                    summary='Duration in percent of AWS Lambda "timeout" limit: 90.24% (warn/crit at 90.00%/95.00%)',
                ),
                Metric("aws_lambda_duration_in_percent", 90.23766666666667, levels=(90.0, 95.0)),
                Result(state=State.OK, summary="Duration with absolute limits: 902 milliseconds"),
                Metric("aws_lambda_duration", 0.9023766666666667, levels=(5.0, 10.0)),
                Result(state=State.OK, summary="Errors: 0.0000/s"),
                Metric(
                    "error_rate", 0.0, levels=(_MORE_THAN_ONE_PER_HOUR, _MORE_THAN_ONE_PER_HOUR)
                ),
                Result(state=State.OK, summary="Invocations: 0.0050/s"),
                Metric("aws_lambda_invocations", 0.005),
                Result(state=State.OK, summary="Throttles: 0.0000/s"),
                Metric(
                    "aws_lambda_throttles",
                    0.0,
                    levels=(_MORE_THAN_ONE_PER_HOUR, _MORE_THAN_ONE_PER_HOUR),
                ),
                Result(state=State.OK, summary="Init duration with absolute limits: 2 seconds"),
                Metric("aws_lambda_init_duration_absolute", 1.62853),
                Result(
                    state=State.CRIT,
                    summary="Cold starts in percent: 50.00% (warn/crit at 10.00%/20.00%)",
                ),
                Metric("aws_lambda_cold_starts_in_percent", 50.0, levels=(10.0, 20.0)),
            ],
        ),
    ],
)
def test_check_aws_lambda_performance(
    item,
    params: LambdaPerformanceParameters,
    section_aws_lambda_summary: Optional[LambdaSummarySection],
    section_aws_lambda: Optional[LambdaCloudwatchSection],
    section_aws_lambda_cloudwatch_insights: Optional[CloudwatchInsightsSection],
    results: CheckResult,
) -> None:
    assert (
        list(
            check_aws_lambda_performance(
                item,
                params,
                section_aws_lambda_summary,
                section_aws_lambda,
                section_aws_lambda_cloudwatch_insights,
            )
        )
        == results
    )


@pytest.mark.parametrize(
    "section_aws_lambda_summary, section_aws_lambda, section_aws_lambda_cloudwatch_insights, results",
    [
        (
            None,
            None,
            None,
            [],
        ),
        (
            SECTION_AWS_LAMBDA_SUMMARY,
            _SECTION_AWS_LAMBDA,
            SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS,
            [
                Service(item="eu-central-1 calling_other_lambda_concurrently"),
                Service(item="eu-central-1 my_python_test_function"),
                Service(item="eu-north-1 myLambdaTestFunction"),
            ],
        ),
    ],
)
def test_discover_aws_lambda(
    section_aws_lambda_summary: Optional[LambdaSummarySection],
    section_aws_lambda: Optional[LambdaCloudwatchSection],
    section_aws_lambda_cloudwatch_insights: Optional[CloudwatchInsightsSection],
    results: DiscoveryResult,
) -> None:
    assert (
        list(
            discover_aws_lambda(
                section_aws_lambda_summary,
                section_aws_lambda,
                section_aws_lambda_cloudwatch_insights,
            )
        )
        == results
    )
