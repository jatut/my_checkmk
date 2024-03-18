#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# pylint: disable=protected-access

# pylint: disable=redefined-outer-name

from collections.abc import Iterator, Mapping, Sequence
from typing import Any

import pytest
from mypy_boto3_logs.client import CloudWatchLogsClient
from mypy_boto3_logs.type_defs import GetQueryResultsResponseTypeDef

from cmk.special_agents.agent_aws import (
    _create_lamdba_sections,
    AWSConfig,
    LambdaCloudwatch,
    LambdaCloudwatchInsights,
    LambdaProvisionedConcurrency,
    LambdaRegionLimits,
    LambdaSummary,
    NamingConvention,
    OverallTags,
    ResultDistributor,
)

from .agent_aws_fake_clients import (
    Entity,
    FakeCloudwatchClient,
    FakeCloudwatchClientLogsClient,
    LambdaListFunctionsIB,
    LambdaListProvisionedConcurrencyConfigsIB,
    LambdaListTagsInstancesIB,
)


class PaginatorListFunctions:
    def paginate(self) -> Iterator[Mapping[str, Any]]:
        yield {"Functions": LambdaListFunctionsIB.create_instances(2)}


class PaginatorProvisionedConcurrencyConfigs:
    # "FunctionName" must occur in the function signature, but is not used in the current implementation => disable warning
    def paginate(self, FunctionName: str) -> Iterator[Mapping[str, Any]]:
        yield {
            "ProvisionedConcurrencyConfigs": LambdaListProvisionedConcurrencyConfigsIB.create_instances(
                2
            )
        }


class FakeLambdaClient:
    def __init__(self, skip_entities=None) -> None:  # type: ignore[no-untyped-def]
        self._skip_entities = {} if not skip_entities else skip_entities

    def get_paginator(self, operation_name: str) -> Any:
        if operation_name == "list_functions":
            return PaginatorListFunctions()
        if operation_name == "list_provisioned_concurrency_configs":
            return PaginatorProvisionedConcurrencyConfigs()
        return None

    def list_tags(self, Resource: str) -> Mapping[str, Mapping[Entity, Entity]]:
        tags: Mapping[Entity, Entity] = {}
        if Resource == "arn:aws:lambda:eu-central-1:123456789:function:FunctionName-0":
            tags = LambdaListTagsInstancesIB.create_instances(amount=1)
        return {"Tags": tags}

    def get_account_settings(self) -> Mapping[str, Any]:
        return {
            "AccountLimit": {
                "TotalCodeSize": 123,
                "CodeSizeUnzipped": 123,
                "CodeSizeZipped": 123,
                "ConcurrentExecutions": 123,
                "UnreservedConcurrentExecutions": 123,
            },
            "AccountUsage": {"TotalCodeSize": 123, "FunctionCount": 123},
        }


def create_config(names: Sequence[str], tags: OverallTags) -> AWSConfig:
    config = AWSConfig("hostname", [], ([], []), NamingConvention.ip_region_instance)
    config.add_single_service_config("lambda_names", names)
    config.add_service_tags("lambda_tags", tags)
    return config


def get_lambda_sections(names: Sequence[str], tags: OverallTags) -> tuple[
    LambdaRegionLimits,
    LambdaSummary,
    LambdaProvisionedConcurrency,
    LambdaCloudwatch,
    LambdaCloudwatchInsights,
]:
    distributor = ResultDistributor()

    # TODO: FakeLambdaClient shoud actually subclass LambdaClient, etc.
    return _create_lamdba_sections(
        FakeLambdaClient(False),  # type: ignore[arg-type]
        FakeCloudwatchClient(),  # type: ignore[arg-type]
        FakeCloudwatchClientLogsClient(),  # type: ignore[arg-type]
        "region",
        create_config(names, tags),
        distributor,
    )


no_tags_or_names_params = [
    (None, (None, None)),
]

summary_params = [
    (
        None,
        (None, None),
        [
            "FunctionName-0",
            "FunctionName-1",
        ],
    ),
    (
        ["FunctionName-0"],
        (None, None),
        [
            "FunctionName-0",
        ],
    ),
    (
        None,
        ([["Tag-0"]], [["Value-0"]]),
        [
            "FunctionName-0",
        ],
    ),
]


@pytest.mark.parametrize("names,tags", no_tags_or_names_params)
def test_agent_aws_lambda_region_limits(
    names: Sequence[str],
    tags: OverallTags,
) -> None:
    (
        lambda_limits,
        _lambda_summary,
        _lambda_provisioned_concurrency_configuration,
        _lambda_cloudwatch,
        _lambda_cloudwatch_insights,
    ) = get_lambda_sections(names, tags)
    lambda_limits_results = lambda_limits.run()
    assert lambda_limits.cache_interval == 300
    assert lambda_limits.period == 600
    assert lambda_limits.name == "lambda_region_limits"
    assert len(lambda_limits_results[0][0].content) == 3


@pytest.mark.parametrize("names,tags,expected", summary_params)
def test_agent_aws_lambda_summary(
    names: Sequence[str], tags: OverallTags, expected: Sequence[str]
) -> None:
    (
        _lambda_limits,
        lambda_summary,
        lambda_provisioned_concurrency_configuration,
        _lambda_cloudwatch,
        _lambda_cloudwatch_insights,
    ) = get_lambda_sections(names, tags)
    lambda_provisioned_concurrency_configuration.run()
    lambda_summary_results = lambda_summary.run().results

    assert lambda_summary.cache_interval == 300
    assert lambda_summary.period == 600
    assert lambda_summary.name == "lambda_summary"
    assert len(lambda_summary_results) == 1
    for result in lambda_summary_results:
        assert result.piggyback_hostname == ""
        assert [lambda_function["FunctionName"] for lambda_function in result.content] == expected


@pytest.mark.parametrize("names,tags", no_tags_or_names_params)
def test_agent_aws_lambda_cloudwatch(names: Sequence[str], tags: OverallTags) -> None:
    (
        _lambda_limits,
        lambda_summary,
        lambda_provisioned_concurrency_configuration,
        lambda_cloudwatch,
        _lambda_cloudwatch_insights,
    ) = get_lambda_sections(
        names,
        tags,
    )
    lambda_summary.run()
    lambda_provisioned_concurrency_configuration.run()
    # We are asserting that the colleague contents is present because otherwise the test is not
    # checking anything
    assert lambda_cloudwatch._get_colleague_contents().content
    _lambda_cloudwatch_results = lambda_cloudwatch.run().results

    assert lambda_cloudwatch.cache_interval == 300
    assert lambda_cloudwatch.period == 600
    assert lambda_cloudwatch.name == "lambda"
    for result in _lambda_cloudwatch_results:
        assert len(result.content) == 84  # all metrics


@pytest.mark.parametrize("names,tags", no_tags_or_names_params)
def test_agent_aws_lambda_provisioned_concurrency_configuration(
    names: Sequence[str], tags: OverallTags
) -> None:
    (
        _lambda_limits,
        lambda_summary,
        lambda_provisioned_concurrency_configuration,
        _lambda_cloudwatch,
        _lambda_cloudwatch_insights,
    ) = get_lambda_sections(
        names,
        tags,
    )
    lambda_summary.run()
    # We are asserting that the colleague contents is present because otherwise the test is not
    # checking anything
    assert lambda_provisioned_concurrency_configuration._get_colleague_contents().content
    lambda_provisioned_concurrency_configuration_results = (
        lambda_provisioned_concurrency_configuration.run().results
    )

    for result in lambda_provisioned_concurrency_configuration_results:
        for _, provisioned_concurrency_config in result.content.items():
            for alias in provisioned_concurrency_config:
                assert alias["FunctionArn"].find("Alias") != -1


@pytest.mark.parametrize("names,tags", no_tags_or_names_params)
def test_agent_aws_lambda_cloudwatch_insights(names: Sequence[str], tags: OverallTags) -> None:
    (
        _lambda_limits,
        lambda_summary,
        lambda_provisioned_concurrency_configuration,
        _lambda_cloudwatch,
        lambda_cloudwatch_insights,
    ) = get_lambda_sections(
        names,
        tags,
    )
    lambda_summary.run()
    lambda_provisioned_concurrency_configuration.run()
    # We are asserting that the colleague contents is present because otherwise the test is not
    # checking anything
    assert lambda_cloudwatch_insights._get_colleague_contents().content
    lambda_cloudwatch_logs_results = lambda_cloudwatch_insights.run().results

    assert lambda_cloudwatch_insights.cache_interval == 300
    assert lambda_cloudwatch_insights.period == 600
    assert lambda_cloudwatch_insights.name == "lambda_cloudwatch_insights"

    # We should have at least a result otherwise the test is not checking anything
    assert lambda_cloudwatch_logs_results[0].content
    for result in lambda_cloudwatch_logs_results:
        for function_arn, metrics in result.content.items():
            function_name = function_arn.split(":")[-1]
            assert function_name not in {
                "FunctionName-1",  # In the simulation data, the FunctionName-1 log group doesn't exist so we shouldn't have metrics for it
                "deleted-function",  # In the simulation data, deleted-function is a non-existing function with an existing log group
            }
            assert len(metrics) == 4  # all metrics


def test_lambda_cloudwatch_insights_query_results_timeout() -> None:
    class CloudWatchLogsClientStub(CloudWatchLogsClient):
        def __init__(self):  # pylint: disable=super-init-not-called
            pass

        def get_query_results(self, *, queryId: str) -> GetQueryResultsResponseTypeDef:
            return {
                "results": [[]],
                "statistics": {"recordsMatched": 2.0, "recordsScanned": 6.0, "bytesScanned": 710.0},
                "status": "Running",
                "encryptionKey": "I made this up to make mypy happy",
                "ResponseMetadata": {
                    "RequestId": "0bb17f7e-1230-474a-a9dc-93d583a6a01a",
                    "HostId": "I made this up to make mypy happy",
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {},
                    "RetryAttempts": 0,
                },
            }

    client = CloudWatchLogsClientStub()
    result = LambdaCloudwatchInsights.query_results(
        client=client,
        query_id="FakeQueryId",
        timeout_seconds=0.001,
        sleep_duration=0.001,
    )
    assert result is None
