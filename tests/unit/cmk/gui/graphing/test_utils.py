#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# pylint: disable=protected-access

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Literal

import pytest

from tests.unit.cmk.gui.conftest import SetConfig

from cmk.utils.metrics import MetricName

import cmk.gui.graphing._utils as utils
from cmk.gui.config import active_config
from cmk.gui.graphing._expression import CriticalOf, Metric, WarningOf
from cmk.gui.graphing._graph_templates import (
    _compute_predictive_metrics,
    get_graph_templates,
    GraphTemplate,
    MetricDefinition,
    ScalarDefinition,
)
from cmk.gui.graphing._legacy import AutomaticDict, check_metrics, CheckMetricEntry, UnitInfo
from cmk.gui.graphing._metrics import _get_legacy_metric_info
from cmk.gui.graphing._type_defs import Original, TranslatedMetric
from cmk.gui.graphing._utils import (
    find_matching_translation,
    lookup_metric_translations_for_check_command,
    TranslationSpec,
)
from cmk.gui.type_defs import Perfdata, PerfDataTuple
from cmk.gui.utils.temperate_unit import TemperatureUnit


@pytest.mark.usefixtures("request_context")
@pytest.mark.parametrize(
    "perf_str, check_command, result",
    [
        ("", None, ([], "")),
        (
            "he lo=1",
            None,
            (
                [
                    PerfDataTuple("lo", "lo", 1, "", None, None, None, None),
                ],
                "",
            ),
        ),
        (
            "'há li'=2",
            None,
            (
                [
                    PerfDataTuple("há_li", "há_li", 2, "", None, None, None, None),
                ],
                "",
            ),
        ),
        (
            "hé ßß=3",
            None,
            (
                [
                    PerfDataTuple("ßß", "ßß", 3, "", None, None, None, None),
                ],
                "",
            ),
        ),
        (
            "hi=6 [ihe]",
            "ter",
            (
                [
                    PerfDataTuple("hi", "hi", 6, "", None, None, None, None),
                ],
                "ihe",
            ),
        ),
        ("hi=l6 [ihe]", "ter", ([], "ihe")),
        (
            "hi=6 [ihe]",
            "ter",
            (
                [
                    PerfDataTuple("hi", "hi", 6, "", None, None, None, None),
                ],
                "ihe",
            ),
        ),
        (
            "hi=5 no=6",
            "test",
            (
                [
                    PerfDataTuple("hi", "hi", 5, "", None, None, None, None),
                    PerfDataTuple("no", "no", 6, "", None, None, None, None),
                ],
                "test",
            ),
        ),
        (
            "hi=5;6;7;8;9 'not here'=6;5.6;;;",
            "test",
            (
                [
                    PerfDataTuple("hi", "hi", 5, "", 6, 7, 8, 9),
                    PerfDataTuple("not_here", "not_here", 6, "", 5.6, None, None, None),
                ],
                "test",
            ),
        ),
        (
            "hi=5G;;;; 'not here'=6M;5.6;;;",
            "test",
            (
                [
                    PerfDataTuple("hi", "hi", 5, "G", None, None, None, None),
                    PerfDataTuple("not_here", "not_here", 6, "M", 5.6, None, None, None),
                ],
                "test",
            ),
        ),
        (
            "11.26=6;;;;",
            "check_mk-local",
            (
                [
                    PerfDataTuple("11.26", "11.26", 6, "", None, None, None, None),
                ],
                "check_mk-local",
            ),
        ),
    ],
)
def test_parse_perf_data(
    perf_str: str,
    check_command: str | None,
    result: tuple[Perfdata, str],
) -> None:
    assert utils.parse_perf_data(perf_str, check_command, config=active_config) == result


def test_parse_perf_data2(request_context: None, set_config: SetConfig) -> None:
    with pytest.raises(ValueError), set_config(debug=True):
        utils.parse_perf_data("hi ho", None, config=active_config)


@pytest.mark.parametrize(
    "perf_name, check_command, expected_translation_spec",
    [
        (
            "in",
            "check_mk-lnx_if",
            TranslationSpec(
                name="if_in_bps",
                scale=8,
                auto_graph=True,
                deprecated="",
            ),
        ),
        (
            "memused",
            "check_mk-hr_mem",
            TranslationSpec(
                name="mem_lnx_total_used",
                scale=1024**2,
                auto_graph=True,
                deprecated="",
            ),
        ),
        (
            "fake",
            "check_mk-imaginary",
            TranslationSpec(
                name="fake",
                scale=1.0,
                auto_graph=True,
                deprecated="",
            ),
        ),
    ],
)
def test_perfvar_translation(
    perf_name: str, check_command: str, expected_translation_spec: TranslationSpec
) -> None:
    assert (
        find_matching_translation(
            MetricName(perf_name),
            lookup_metric_translations_for_check_command(check_metrics, check_command),
        )
        == expected_translation_spec
    )


@pytest.mark.parametrize(
    ["translations", "expected_result"],
    [
        pytest.param(
            {},
            TranslationSpec(
                name=MetricName("my_metric"),
                scale=1.0,
                auto_graph=True,
                deprecated="",
            ),
            id="no translations",
        ),
        pytest.param(
            {
                MetricName("old_name"): TranslationSpec(
                    name=MetricName("new_name"),
                    scale=1.0,
                    auto_graph=True,
                    deprecated="",
                )
            },
            TranslationSpec(
                name=MetricName("my_metric"),
                scale=1.0,
                auto_graph=True,
                deprecated="",
            ),
            id="no applicable translations",
        ),
        pytest.param(
            {
                MetricName("my_metric"): TranslationSpec(
                    name=MetricName("new_name"),
                    scale=2.0,
                    auto_graph=True,
                    deprecated="",
                ),
                MetricName("other_metric"): TranslationSpec(
                    name=MetricName("other_new_name"),
                    scale=0.1,
                    auto_graph=True,
                    deprecated="",
                ),
            },
            TranslationSpec(
                name=MetricName("new_name"),
                scale=2.0,
                auto_graph=True,
                deprecated="",
            ),
            id="1-to-1 translations",
        ),
        pytest.param(
            {
                MetricName("~.*my_metric"): TranslationSpec(
                    name=MetricName("~.*my_metric"),
                    scale=5.0,
                    auto_graph=True,
                    deprecated="",
                ),
                MetricName("other_metric"): TranslationSpec(
                    name=MetricName("other_new_name"),
                    scale=0.1,
                    auto_graph=True,
                    deprecated="",
                ),
            },
            TranslationSpec(
                name=MetricName("~.*my_metric"),
                scale=5.0,
                auto_graph=True,
                deprecated="",
            ),
            id="regex translations",
        ),
    ],
)
def test_find_matching_translation(
    translations: Mapping[MetricName, TranslationSpec],
    expected_result: TranslationSpec,
) -> None:
    assert find_matching_translation(MetricName("my_metric"), translations) == expected_result


@pytest.mark.parametrize(
    "metric_names, check_command, graph_ids",
    [
        (["user", "system", "wait", "util"], "check_mk-kernel_util", ["cpu_utilization_5_util"]),
        (["util1", "util15"], "check_mk-kernel_util", ["util_average_2"]),
        (["util"], "check_mk-kernel_util", ["util_fallback"]),
        (["util"], "check_mk-lxc_container_cpu", ["util_fallback"]),
        (
            ["wait", "util", "user", "system"],
            "check_mk-lxc_container_cpu",
            ["cpu_utilization_5_util"],
        ),
        (["util", "util_average"], "check_mk-kernel_util", ["util_average_1"]),
        (["user", "util_numcpu_as_max"], "check_mk-kernel_util", ["cpu_utilization_numcpus"]),
        (
            ["user", "util"],
            "check_mk-kernel_util",
            ["util_fallback", "METRIC_user"],
        ),  # METRIC_user has no recipe
        (["user", "util"], "check_mk-winperf_processor_util", ["cpu_utilization_numcpus"]),
        (["user", "system", "idle", "nice"], "check_mk-kernel_util", ["cpu_utilization_3"]),
        (["user", "system", "idle", "io_wait"], "check_mk-kernel_util", ["cpu_utilization_4"]),
        (["user", "system", "io_wait"], "check_mk-kernel_util", ["cpu_utilization_5"]),
        (
            ["util_average", "util", "wait", "user", "system", "guest"],
            "check_mk-kernel_util",
            ["cpu_utilization_6_guest_util"],
        ),
        (
            ["user", "system", "io_wait", "guest", "steal"],
            "check_mk-statgrab_cpu",
            ["cpu_utilization_6_guest", "cpu_utilization_7"],
        ),
        (["user", "system", "interrupt"], "check_mk-kernel_util", ["cpu_utilization_8"]),
        (
            ["user", "system", "wait", "util", "cpu_entitlement", "cpu_entitlement_util"],
            "check_mk-lparstat_aix_cpu_util",
            ["cpu_entitlement", "cpu_utilization_5_util"],
        ),
        (
            ["ramused", "swapused", "memused"],
            "check_mk-statgrab_mem",
            ["METRIC_mem_lnx_total_used", "METRIC_mem_used", "METRIC_swap_used"],
        ),
        (
            [
                "aws_ec2_running_ondemand_instances_total",
                "aws_ec2_running_ondemand_instances_t2.micro",
                "aws_ec2_running_ondemand_instances_t2.nano",
            ],
            "check_mk-aws_ec2_limits",
            ["aws_ec2_running_ondemand_instances_t2", "aws_ec2_running_ondemand_instances"],
        ),
    ],
)
def test_get_graph_templates_1(
    metric_names: Sequence[str],
    check_command: str,
    graph_ids: Sequence[str],
    request_context: None,
) -> None:
    perfdata: Perfdata = [PerfDataTuple(n, n, 0, "", None, None, None, None) for n in metric_names]
    translated_metrics = utils.translate_metrics(perfdata, check_command)
    assert sorted([t.id for t in get_graph_templates(translated_metrics)]) == sorted(graph_ids)


@pytest.mark.parametrize(
    "metric_names, warn_crit_min_max, check_command, graph_ids",
    [
        pytest.param(
            ["ramused", "swapused", "memused"],
            (0, 1, 2, 3),
            "check_mk-statgrab_mem",
            ["METRIC_mem_lnx_total_used", "ram_swap_used"],
            id="ram_swap_used",
        ),
    ],
)
def test_get_graph_templates_2(
    metric_names: Sequence[str],
    warn_crit_min_max: tuple[int, int, int, int],
    check_command: str,
    graph_ids: Sequence[str],
    request_context: None,
) -> None:
    perfdata: Perfdata = [PerfDataTuple(n, n, 0, "", *warn_crit_min_max) for n in metric_names]
    translated_metrics = utils.translate_metrics(perfdata, check_command)
    assert sorted([t.id for t in get_graph_templates(translated_metrics)]) == sorted(graph_ids)


@pytest.mark.parametrize(
    "metric_definitions, expected_predictive_metric_definitions",
    [
        pytest.param(
            [],
            [],
            id="empty",
        ),
        pytest.param(
            [MetricDefinition(expression=Metric(name="metric_name"), line_type="line")],
            [
                MetricDefinition(expression=Metric(name="predict_metric_name"), line_type="line"),
                MetricDefinition(
                    expression=Metric(name="predict_lower_metric_name"), line_type="line"
                ),
            ],
            id="line",
        ),
        pytest.param(
            [MetricDefinition(expression=Metric(name="metric_name"), line_type="area")],
            [
                MetricDefinition(expression=Metric(name="predict_metric_name"), line_type="line"),
                MetricDefinition(
                    expression=Metric(name="predict_lower_metric_name"), line_type="line"
                ),
            ],
            id="area",
        ),
        pytest.param(
            [MetricDefinition(expression=Metric(name="metric_name"), line_type="stack")],
            [
                MetricDefinition(expression=Metric(name="predict_metric_name"), line_type="line"),
                MetricDefinition(
                    expression=Metric(name="predict_lower_metric_name"), line_type="line"
                ),
            ],
            id="stack",
        ),
        pytest.param(
            [MetricDefinition(expression=Metric(name="metric_name"), line_type="-line")],
            [
                MetricDefinition(expression=Metric(name="predict_metric_name"), line_type="-line"),
                MetricDefinition(
                    expression=Metric(name="predict_lower_metric_name"), line_type="-line"
                ),
            ],
            id="-line",
        ),
        pytest.param(
            [MetricDefinition(expression=Metric(name="metric_name"), line_type="-area")],
            [
                MetricDefinition(expression=Metric(name="predict_metric_name"), line_type="-line"),
                MetricDefinition(
                    expression=Metric(name="predict_lower_metric_name"), line_type="-line"
                ),
            ],
            id="-area",
        ),
        pytest.param(
            [MetricDefinition(expression=Metric(name="metric_name"), line_type="-stack")],
            [
                MetricDefinition(expression=Metric(name="predict_metric_name"), line_type="-line"),
                MetricDefinition(
                    expression=Metric(name="predict_lower_metric_name"), line_type="-line"
                ),
            ],
            id="-stack",
        ),
    ],
)
def test__compute_predictive_metrics(
    metric_definitions: Sequence[MetricDefinition],
    expected_predictive_metric_definitions: Sequence[MetricDefinition],
) -> None:
    assert (
        list(
            _compute_predictive_metrics(
                {
                    "metric_name": TranslatedMetric(
                        originals=[Original("metric_name", 1.0)],
                        value=0.0,
                        scalar={},
                        auto_graph=True,
                        title="",
                        unit_info=UnitInfo(
                            id="id",
                            title="Title",
                            symbol="",
                            render=lambda v: f"{v}",
                            js_render="v => v",
                            conversion=lambda v: v,
                        ),
                        color="#0080c0",
                    ),
                    "predict_metric_name": TranslatedMetric(
                        originals=[Original("predict_metric_name", 1.0)],
                        value=0.0,
                        scalar={},
                        auto_graph=True,
                        title="",
                        unit_info=UnitInfo(
                            id="id",
                            title="Title",
                            symbol="",
                            render=lambda v: f"{v}",
                            js_render="v => v",
                            conversion=lambda v: v,
                        ),
                        color="#0080c0",
                    ),
                    "predict_lower_metric_name": TranslatedMetric(
                        originals=[Original("predict_lower_metric_name", 1.0)],
                        value=0.0,
                        scalar={},
                        auto_graph=True,
                        title="",
                        unit_info=UnitInfo(
                            id="id",
                            title="Title",
                            symbol="",
                            render=lambda v: f"{v}",
                            js_render="v => v",
                            conversion=lambda v: v,
                        ),
                        color="#0080c0",
                    ),
                },
                metric_definitions,
            )
        )
        == expected_predictive_metric_definitions
    )


def test__get_legacy_metric_info() -> None:
    color_counter: Counter[Literal["metric", "predictive"]] = Counter()
    assert _get_legacy_metric_info("foo", color_counter) == {
        "title": "Foo",
        "unit": "",
        "color": "12/a",
    }
    assert _get_legacy_metric_info("bar", color_counter) == {
        "title": "Bar",
        "unit": "",
        "color": "13/a",
    }
    assert color_counter["metric"] == 2


@pytest.mark.parametrize(
    "metric_name, predictive_metric_name, expected_title, expected_color",
    [
        pytest.param(
            "messages_outbound",
            "predict_messages_outbound",
            "Prediction of Outbound messages (upper levels)",
            "#4b4b4b",
            id="upper",
        ),
        pytest.param(
            "messages_outbound",
            "predict_lower_messages_outbound",
            "Prediction of Outbound messages (lower levels)",
            "#4b4b4b",
            id="lower",
        ),
    ],
)
def test_translate_metrics_with_predictive_metrics(
    metric_name: str,
    predictive_metric_name: str,
    expected_title: str,
    expected_color: str,
) -> None:
    perfdata: Perfdata = [
        PerfDataTuple(metric_name, metric_name, 0, "", None, None, None, None),
        PerfDataTuple(predictive_metric_name, metric_name, 0, "", None, None, None, None),
    ]
    translated_metrics = utils.translate_metrics(perfdata, "my-check-plugin")
    assert translated_metrics[predictive_metric_name].title == expected_title

    predictive_unit_info = translated_metrics[predictive_metric_name].unit_info
    expected_unit_info = translated_metrics[metric_name].unit_info
    assert predictive_unit_info.id == expected_unit_info.id
    assert predictive_unit_info.title == expected_unit_info.title
    assert predictive_unit_info.symbol == expected_unit_info.symbol
    assert predictive_unit_info.js_render == expected_unit_info.js_render
    assert predictive_unit_info.stepping == expected_unit_info.stepping
    assert predictive_unit_info.color == expected_unit_info.color
    assert predictive_unit_info.graph_unit == expected_unit_info.graph_unit
    assert predictive_unit_info.description == expected_unit_info.description
    assert predictive_unit_info.valuespec == expected_unit_info.valuespec
    assert predictive_unit_info.perfometer_render == expected_unit_info.perfometer_render
    assert predictive_unit_info.formatter_ident == expected_unit_info.formatter_ident
    assert predictive_unit_info.conversion(123.456) == 123.456

    assert translated_metrics[predictive_metric_name].color == expected_color


def test_translate_metrics_with_multiple_predictive_metrics() -> None:
    perfdata: Perfdata = [
        PerfDataTuple("messages_outbound", "messages_outbound", 0, "", None, None, None, None),
        PerfDataTuple(
            "predict_messages_outbound", "messages_outbound", 0, "", None, None, None, None
        ),
        PerfDataTuple(
            "predict_lower_messages_outbound", "messages_outbound", 0, "", None, None, None, None
        ),
    ]
    translated_metrics = utils.translate_metrics(perfdata, "my-check-plugin")
    assert translated_metrics["predict_messages_outbound"].color == "#4b4b4b"
    assert translated_metrics["predict_lower_messages_outbound"].color == "#5a5a5a"


@pytest.mark.parametrize(
    "metric_names, predict_metric_names, predict_lower_metric_names, check_command, graph_templates",
    [
        pytest.param(
            [
                "messages_outbound",
                "messages_inbound",
            ],
            [
                "predict_messages_outbound",
                "predict_messages_inbound",
            ],
            [
                "predict_lower_messages_outbound",
                "predict_lower_messages_inbound",
            ],
            "check_mk-inbound_and_outbound_messages",
            [
                GraphTemplate(
                    id="inbound_and_outbound_messages",
                    title="Inbound and Outbound Messages",
                    scalars=[],
                    conflicting_metrics=(),
                    optional_metrics=(),
                    consolidation_function=None,
                    range=None,
                    omit_zero_metrics=False,
                    metrics=[
                        MetricDefinition(
                            expression=Metric(name="messages_outbound"),
                            line_type="stack",
                            title="Outbound messages",
                        ),
                        MetricDefinition(
                            expression=Metric(name="messages_inbound"),
                            line_type="stack",
                            title="Inbound messages",
                        ),
                        MetricDefinition(
                            expression=Metric(name="predict_messages_outbound"),
                            line_type="line",
                        ),
                        MetricDefinition(
                            expression=Metric(name="predict_lower_messages_outbound"),
                            line_type="line",
                        ),
                        MetricDefinition(
                            expression=Metric(name="predict_messages_inbound"),
                            line_type="line",
                        ),
                        MetricDefinition(
                            expression=Metric(name="predict_lower_messages_inbound"),
                            line_type="line",
                        ),
                    ],
                )
            ],
            id="matches",
        ),
        pytest.param(
            [
                "messages_outbound",
                "messages_inbound",
                "foo",
            ],
            [
                "predict_foo",
            ],
            [
                "predict_lower_foo",
            ],
            "check_mk-inbound_and_outbound_messages",
            [
                GraphTemplate(
                    id="inbound_and_outbound_messages",
                    title="Inbound and Outbound Messages",
                    scalars=[],
                    conflicting_metrics=(),
                    optional_metrics=(),
                    consolidation_function=None,
                    range=None,
                    omit_zero_metrics=False,
                    metrics=[
                        MetricDefinition(
                            expression=Metric(name="messages_outbound"),
                            line_type="stack",
                            title="Outbound messages",
                        ),
                        MetricDefinition(
                            expression=Metric(name="messages_inbound"),
                            line_type="stack",
                            title="Inbound messages",
                        ),
                    ],
                ),
                GraphTemplate(
                    id="METRIC_foo",
                    title="",
                    scalars=[
                        ScalarDefinition(
                            expression=WarningOf(metric=Metric(name="foo")),
                            title="Warning",
                        ),
                        ScalarDefinition(
                            expression=CriticalOf(metric=Metric(name="foo")),
                            title="Critical",
                        ),
                    ],
                    conflicting_metrics=[],
                    optional_metrics=[],
                    consolidation_function=None,
                    range=None,
                    omit_zero_metrics=False,
                    metrics=[
                        MetricDefinition(
                            expression=Metric(name="foo"),
                            line_type="area",
                        )
                    ],
                ),
                GraphTemplate(
                    id="METRIC_predict_foo",
                    title="",
                    scalars=[
                        ScalarDefinition(
                            expression=WarningOf(metric=Metric(name="predict_foo")),
                            title="Warning",
                        ),
                        ScalarDefinition(
                            expression=CriticalOf(metric=Metric(name="predict_foo")),
                            title="Critical",
                        ),
                    ],
                    conflicting_metrics=[],
                    optional_metrics=[],
                    consolidation_function=None,
                    range=None,
                    omit_zero_metrics=False,
                    metrics=[
                        MetricDefinition(
                            expression=Metric(name="predict_foo"),
                            line_type="area",
                        )
                    ],
                ),
                GraphTemplate(
                    id="METRIC_predict_lower_foo",
                    title="",
                    scalars=[
                        ScalarDefinition(
                            expression=WarningOf(metric=Metric(name="predict_lower_foo")),
                            title="Warning",
                        ),
                        ScalarDefinition(
                            expression=CriticalOf(metric=Metric(name="predict_lower_foo")),
                            title="Critical",
                        ),
                    ],
                    conflicting_metrics=[],
                    optional_metrics=[],
                    consolidation_function=None,
                    range=None,
                    omit_zero_metrics=False,
                    metrics=[
                        MetricDefinition(
                            expression=Metric(name="predict_lower_foo"),
                            line_type="area",
                        )
                    ],
                ),
            ],
            id="does-not-match",
        ),
    ],
)
def test_get_graph_templates_with_predictive_metrics(
    metric_names: Sequence[str],
    predict_metric_names: Sequence[str],
    predict_lower_metric_names: Sequence[str],
    check_command: str,
    graph_templates: Sequence[GraphTemplate],
    request_context: None,
) -> None:
    perfdata: Perfdata = (
        [PerfDataTuple(n, n, 0, "", None, None, None, None) for n in metric_names]
        + [PerfDataTuple(n, n[8:], 0, "", None, None, None, None) for n in predict_metric_names]
        + [
            PerfDataTuple(n, n[14:], 0, "", None, None, None, None)
            for n in predict_lower_metric_names
        ]
    )
    translated_metrics = utils.translate_metrics(perfdata, check_command)
    found_graph_templates = list(get_graph_templates(translated_metrics))
    assert found_graph_templates == graph_templates


@pytest.mark.parametrize(
    "metric_names, graph_ids",
    [
        # cpu.py
        pytest.param(
            ["user_time", "children_user_time", "system_time", "children_system_time"],
            ["used_cpu_time"],
            id="used_cpu_time",
        ),
        pytest.param(
            [
                "user_time",
                "children_user_time",
                "system_time",
                "children_system_time",
                "cmk_time_agent",
                "cmk_time_snmp",
                "cmk_time_ds",
            ],
            [
                "METRIC_children_system_time",
                "METRIC_children_user_time",
                "METRIC_cmk_time_agent",
                "METRIC_cmk_time_ds",
                "METRIC_cmk_time_snmp",
                "METRIC_system_time",
                "METRIC_user_time",
            ],
            id="used_cpu_time_conflicting_metrics",
        ),
        pytest.param(
            ["user_time", "system_time"],
            ["cpu_time"],
            id="cpu_time",
        ),
        pytest.param(
            ["user_time", "system_time", "children_user_time"],
            ["METRIC_children_user_time", "METRIC_system_time", "METRIC_user_time"],
            id="cpu_time_conflicting_metrics",
        ),
        pytest.param(
            ["util", "util_average"],
            ["util_average_1"],
            id="util_average_1",
        ),
        pytest.param(
            [
                "util",
                "util_average",
                "util_average_1",
                "idle",
                "cpu_util_guest",
                "cpu_util_steal",
                "io_wait",
                "user",
                "system",
            ],
            ["cpu_utilization_4", "cpu_utilization_7_util", "METRIC_util_average_1"],
            id="util_average_1_conflicting_metrics",
        ),
        pytest.param(
            ["user", "system", "util_average", "util"],
            ["cpu_utilization_simple"],
            id="cpu_utilization_simple",
        ),
        pytest.param(
            [
                "user",
                "system",
                "util_average",
                "util",
                "idle",
                "cpu_util_guest",
                "cpu_util_steal",
                "io_wait",
            ],
            ["cpu_utilization_4", "cpu_utilization_7_util"],
            id="cpu_utilization_simple_conflicting_metrics",
        ),
        pytest.param(
            ["user", "system", "io_wait", "util_average"],
            ["cpu_utilization_5"],
            id="cpu_utilization_5",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "util_average",
                "util",
                "idle",
                "cpu_util_guest",
                "cpu_util_steal",
            ],
            ["cpu_utilization_4", "cpu_utilization_7_util"],
            id="cpu_utilization_5_conflicting_metrics",
        ),
        # cpu_utilization_5_util
        pytest.param(
            ["user", "system", "io_wait", "util_average", "util"],
            ["cpu_utilization_5_util"],
            id="cpu_utilization_5_util",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "util_average",
                "util",
                "cpu_util_guest",
                "cpu_util_steal",
            ],
            ["cpu_utilization_7_util"],
            id="cpu_utilization_5_util_conflicting_metrics",
        ),
        pytest.param(
            ["user", "system", "io_wait", "cpu_util_steal", "util_average"],
            ["cpu_utilization_6_steal"],
            id="cpu_utilization_6_steal",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "cpu_util_steal",
                "util_average",
                "util",
                "cpu_util_guest",
            ],
            ["cpu_utilization_7_util"],
            id="cpu_utilization_6_steal_conflicting_metrics",
        ),
        pytest.param(
            ["user", "system", "io_wait", "cpu_util_steal", "util_average", "util"],
            ["cpu_utilization_6_steal_util"],
            id="cpu_utilization_6_steal_util",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "cpu_util_steal",
                "util_average",
                "util",
                "cpu_util_guest",
            ],
            ["cpu_utilization_7_util"],
            id="cpu_utilization_6_steal_util_conflicting_metrics",
        ),
        pytest.param(
            ["user", "system", "io_wait", "cpu_util_guest", "util_average", "cpu_util_steal"],
            ["cpu_utilization_6_guest", "cpu_utilization_7"],
            id="cpu_utilization_6_guest",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "cpu_util_guest",
                "util_average",
                "cpu_util_steal",
                "util",
            ],
            ["cpu_utilization_7_util"],
            id="cpu_utilization_6_guest_conflicting_metrics",
        ),
        pytest.param(
            ["user", "system", "io_wait", "cpu_util_guest", "util_average", "util"],
            ["cpu_utilization_6_guest_util"],
            id="cpu_utilization_6_guest_util",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "cpu_util_guest",
                "util_average",
                "util",
                "cpu_util_steal",
            ],
            ["cpu_utilization_7_util"],
            id="cpu_utilization_6_guest_util_conflicting_metrics",
        ),
        #
        pytest.param(
            ["user", "system", "io_wait", "cpu_util_guest", "cpu_util_steal", "util_average"],
            ["cpu_utilization_6_guest", "cpu_utilization_7"],
            id="cpu_utilization_7",
        ),
        pytest.param(
            [
                "user",
                "system",
                "io_wait",
                "cpu_util_guest",
                "cpu_util_steal",
                "util_average",
                "util",
            ],
            ["cpu_utilization_7_util"],
            id="cpu_utilization_7_conflicting_metrics",
        ),
        pytest.param(
            ["util"],
            ["util_fallback"],
            id="util_fallback",
        ),
        pytest.param(
            ["util", "util_average", "system", "engine_cpu_util"],
            ["cpu_utilization", "METRIC_system", "METRIC_util_average"],
            id="util_fallback_conflicting_metrics",
        ),
        # fs.py
        pytest.param(
            ["fs_used", "fs_size"],
            ["fs_used"],
            id="fs_used",
        ),
        pytest.param(
            ["fs_used", "fs_size", "reserved"],
            ["METRIC_fs_size", "METRIC_fs_used", "METRIC_reserved"],
            id="fs_used_conflicting_metrics",
        ),
        # mail.py
        pytest.param(
            ["mail_queue_deferred_length", "mail_queue_active_length"],
            ["amount_of_mails_in_queues"],
            id="amount_of_mails_in_queues",
        ),
        pytest.param(
            [
                "mail_queue_deferred_length",
                "mail_queue_active_length",
                "mail_queue_postfix_total",
                "mail_queue_z1_messenger",
            ],
            [
                "METRIC_mail_queue_active_length",
                "METRIC_mail_queue_deferred_length",
                "METRIC_mail_queue_postfix_total",
                "METRIC_mail_queue_z1_messenger",
            ],
            id="amount_of_mails_in_queues_conflicting_metrics",
        ),
        pytest.param(
            ["mail_queue_deferred_size", "mail_queue_active_size"],
            ["size_of_mails_in_queues"],
            id="size_of_mails_in_queues",
        ),
        pytest.param(
            [
                "mail_queue_deferred_size",
                "mail_queue_active_size",
                "mail_queue_postfix_total",
                "mail_queue_z1_messenger",
            ],
            [
                "METRIC_mail_queue_active_size",
                "METRIC_mail_queue_deferred_size",
                "METRIC_mail_queue_postfix_total",
                "METRIC_mail_queue_z1_messenger",
            ],
            id="size_of_mails_in_queues_conflicting_metrics",
        ),
        pytest.param(
            ["mail_queue_hold_length", "mail_queue_incoming_length", "mail_queue_drop_length"],
            ["amount_of_mails_in_secondary_queues"],
            id="amount_of_mails_in_secondary_queues",
        ),
        pytest.param(
            [
                "mail_queue_hold_length",
                "mail_queue_incoming_length",
                "mail_queue_drop_length",
                "mail_queue_postfix_total",
                "mail_queue_z1_messenger",
            ],
            [
                "METRIC_mail_queue_drop_length",
                "METRIC_mail_queue_hold_length",
                "METRIC_mail_queue_incoming_length",
                "METRIC_mail_queue_postfix_total",
                "METRIC_mail_queue_z1_messenger",
            ],
            id="amount_of_mails_in_secondary_queues_conflicting_metrics",
        ),
        # storage.py
        pytest.param(
            ["mem_used", "swap_used"],
            ["METRIC_mem_used", "METRIC_swap_used"],
            id="ram_used_conflicting_metrics",
        ),
        pytest.param(
            ["mem_used", "swap_used", "swap_total"],
            ["METRIC_mem_used", "METRIC_swap_total", "METRIC_swap_used"],
            id="ram_swap_used_conflicting_metrics",
        ),
        pytest.param(
            ["mem_lnx_active", "mem_lnx_inactive"],
            ["active_and_inactive_memory"],
            id="active_and_inactive_memory",
        ),
        pytest.param(
            ["mem_lnx_active", "mem_lnx_inactive", "mem_lnx_active_anon"],
            [
                "METRIC_mem_lnx_active",
                "METRIC_mem_lnx_active_anon",
                "METRIC_mem_lnx_inactive",
            ],
            id="active_and_inactive_memory_conflicting_metrics",
        ),
        pytest.param(
            ["mem_used"],
            ["ram_used"],
            id="ram_used",
        ),
        pytest.param(
            ["mem_heap", "mem_nonheap"],
            ["heap_and_non_heap_memory"],
            id="heap_and_non_heap_memory",
        ),
        pytest.param(
            ["mem_heap", "mem_nonheap", "mem_heap_committed", "mem_nonheap_committed"],
            ["heap_memory_usage", "non-heap_memory_usage"],
            id="heap_and_non_heap_memory_conflicting_metrics",
        ),
    ],
)
def test_conflicting_metrics(
    metric_names: Sequence[str],
    graph_ids: Sequence[str],
    request_context: None,
) -> None:
    # Hard to find all avail metric names of a check plug-in.
    # We test conflicting metrics as following:
    # 1. write test for expected metric names of a graph template if it has "conflicting_metrics"
    # 2. use metric names from (1) and conflicting metrics
    perfdata: Perfdata = [PerfDataTuple(n, n, 0, "", None, None, None, None) for n in metric_names]
    translated_metrics = utils.translate_metrics(perfdata, "check_command")
    assert sorted([t.id for t in get_graph_templates(translated_metrics)]) == sorted(graph_ids)


@pytest.mark.parametrize(
    ["default_temperature_unit", "expected_value", "expected_scalars"],
    [
        pytest.param(
            TemperatureUnit.CELSIUS,
            59.05,
            {"warn": 85.05, "crit": 85.05},
            id="no unit conversion",
        ),
        pytest.param(
            TemperatureUnit.FAHRENHEIT,
            138.29,
            {"warn": 185.09, "crit": 185.09},
            id="with unit conversion",
        ),
    ],
)
def test_translate_metrics(
    default_temperature_unit: TemperatureUnit,
    expected_value: float,
    expected_scalars: Mapping[str, float],
    request_context: None,
) -> None:
    active_config.default_temperature_unit = default_temperature_unit.value
    translated_metric = utils.translate_metrics(
        [PerfDataTuple("temp", "temp", 59.05, "", 85.05, 85.05, None, None)],
        "check_mk-lnx_thermal",
    )["temp"]
    assert translated_metric.value == expected_value
    assert translated_metric.scalar == expected_scalars


@pytest.mark.parametrize(
    ["translations", "check_command", "expected_result"],
    [
        pytest.param(
            {},
            "check_mk-x",
            {},
            id="no matching entry",
        ),
        pytest.param(
            {
                "check_mk-x": {MetricName("old"): {"name": MetricName("new")}},
                "check_mk-y": {MetricName("a"): {"scale": 2}},
            },
            "check_mk-x",
            {
                MetricName("old"): TranslationSpec(
                    name=MetricName("new"),
                    scale=1.0,
                    auto_graph=True,
                    deprecated="",
                )
            },
            id="standard check",
        ),
        pytest.param(
            {
                "check_mk-x": {MetricName("old"): {"name": MetricName("new")}},
                "check_mk-y": {MetricName("a"): {"scale": 2}},
            },
            "check_mk-mgmt_x",
            {
                MetricName("old"): TranslationSpec(
                    name=MetricName("new"),
                    scale=1.0,
                    auto_graph=True,
                    deprecated="",
                )
            },
            id="management board, fallback to standard check",
        ),
        pytest.param(
            {
                "check_mk_x": {MetricName("old"): {"name": MetricName("new")}},
                "check_mk-mgmt_x": {MetricName("old"): {"scale": 3}},
            },
            "check_mk-mgmt_x",
            {
                MetricName("old"): TranslationSpec(
                    name="old",
                    scale=3,
                    auto_graph=True,
                    deprecated="",
                )
            },
            id="management board, explicit entry",
        ),
        pytest.param(
            {
                "check_mk-x": {MetricName("old"): {"name": MetricName("new")}},
                "check_mk-y": {MetricName("a"): {"scale": 2}},
            },
            None,
            {},
            id="no check command",
        ),
    ],
)
def test_lookup_metric_translations_for_check_command(
    translations: Mapping[str, Mapping[MetricName, CheckMetricEntry]],
    check_command: str | None,
    expected_result: Mapping[MetricName, TranslationSpec],
) -> None:
    metric_translations = lookup_metric_translations_for_check_command(translations, check_command)
    assert metric_translations == expected_result


def test_automatic_dict_append() -> None:
    automatic_dict = AutomaticDict(list_identifier="appended")
    automatic_dict["graph_1"] = {
        "metrics": [
            ("some_metric", "line"),
            ("some_other_metric", "-area"),
        ],
    }
    automatic_dict["graph_2"] = {
        "metrics": [
            ("something", "line"),
        ],
    }
    automatic_dict.append(
        {
            "metrics": [
                ("abc", "line"),
            ],
        }
    )
    automatic_dict.append(
        {
            "metrics": [
                ("xyz", "line"),
            ],
        }
    )
    automatic_dict.append(
        {
            "metrics": [
                ("xyz", "line"),
            ],
        }
    )
    assert dict(automatic_dict) == {
        "appended_0": {
            "metrics": [("abc", "line")],
        },
        "appended_1": {
            "metrics": [("xyz", "line")],
        },
        "graph_1": {
            "metrics": [
                ("some_metric", "line"),
                ("some_other_metric", "-area"),
            ],
        },
        "graph_2": {
            "metrics": [("something", "line")],
        },
    }


@pytest.mark.parametrize(
    "check_command, expected",
    [
        pytest.param(
            "check-mk-custom!foobar",
            "check-mk-custom",
            id="custom-foobar",
        ),
        pytest.param(
            "check-mk-custom!check_ping",
            "check_ping",
            id="custom-check_ping",
        ),
        pytest.param(
            "check-mk-custom!./check_ping",
            "check_ping",
            id="custom-check_ping-2",
        ),
    ],
)
def test__parse_check_command(check_command: str, expected: str) -> None:
    assert utils._parse_check_command(check_command) == expected
