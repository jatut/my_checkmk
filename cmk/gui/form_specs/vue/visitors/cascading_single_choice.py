#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Any

from cmk.gui.form_specs.private import CascadingSingleChoiceExtended
from cmk.gui.form_specs.vue.validators import build_vue_validators
from cmk.gui.i18n import translate_to_current_language

from cmk.rulesets.v1 import Title
from cmk.shared_typing import vue_formspec_components as shared_type_defs

from ._base import FormSpecVisitor
from ._registry import get_visitor
from ._type_defs import DEFAULT_VALUE, DefaultValue, INVALID_VALUE, InvalidValue
from ._utils import (
    base_i18n_form_spec,
    compute_label,
    compute_title_input_hint,
    compute_validation_errors,
    compute_validators,
    create_validation_error,
    get_prefill_default,
    get_title_and_help,
)


class CascadingSingleChoiceVisitor(
    FormSpecVisitor[CascadingSingleChoiceExtended, tuple[str, object]]
):
    def _parse_value(self, raw_value: object) -> tuple[str, object] | InvalidValue:
        if isinstance(raw_value, DefaultValue):
            if isinstance(
                prefill_default := get_prefill_default(self.form_spec.prefill), InvalidValue
            ):
                return prefill_default
            # The default value for a cascading_single_choice element only
            # contains the name of the selected element, not the value.
            return (prefill_default, DEFAULT_VALUE)
        if not isinstance(raw_value, (list, tuple)) or len(raw_value) != 2:
            return INVALID_VALUE

        name = raw_value[0]
        if not any(name == element.name for element in self.form_spec.elements):
            return INVALID_VALUE

        assert isinstance(name, str)
        assert len(raw_value) == 2
        return tuple(raw_value)

    def _to_vue(
        self, raw_value: object, parsed_value: tuple[str, object] | InvalidValue
    ) -> tuple[shared_type_defs.CascadingSingleChoice, tuple[str, object]]:
        title, help_text = get_title_and_help(self.form_spec)
        if isinstance(parsed_value, InvalidValue):
            parsed_value = ("", None)

        selected_name, selected_value = parsed_value
        vue_elements = []
        for element in self.form_spec.elements:
            element_visitor = get_visitor(element.parameter_form, self.options)
            element_value = selected_value if selected_name == element.name else DEFAULT_VALUE
            element_schema, element_vue_value = element_visitor.to_vue(element_value)

            if selected_name == element.name:
                selected_value = element_vue_value

            vue_elements.append(
                shared_type_defs.CascadingSingleChoiceElement(
                    name=element.name,
                    title=element.title.localize(translate_to_current_language),
                    default_value=element_vue_value,
                    parameter_form=element_schema,
                )
            )

        return (
            shared_type_defs.CascadingSingleChoice(
                title=title,
                label=compute_label(self.form_spec.label),
                help=help_text,
                i18n_base=base_i18n_form_spec(),
                elements=vue_elements,
                validators=build_vue_validators(compute_validators(self.form_spec)),
                input_hint=compute_title_input_hint(self.form_spec.prefill),
                layout=self.form_spec.layout,
            ),
            (selected_name, selected_value),
        )

    def _validate(
        self, raw_value: object, parsed_value: tuple[str, object] | InvalidValue
    ) -> list[shared_type_defs.ValidationMessage]:
        if isinstance(parsed_value, InvalidValue):
            return create_validation_error(raw_value, Title("Invalid selection"))

        selected_name, selected_value = parsed_value
        element_validations = (
            compute_validation_errors(compute_validators(self.form_spec), parsed_value)
            if self.form_spec.custom_validate
            else []
        )

        for element in self.form_spec.elements:
            if selected_name != element.name:
                continue

            element_visitor = get_visitor(element.parameter_form, self.options)
            for validation in element_visitor.validate(selected_value):
                element_validations.append(
                    shared_type_defs.ValidationMessage(
                        location=[element.name] + validation.location,
                        message=validation.message,
                        invalid_value=validation.invalid_value,
                    )
                )

        return element_validations

    def _to_disk(self, raw_value: object, parsed_value: tuple[str, object]) -> tuple[str, object]:
        selected_name, selected_value = parsed_value

        disk_value: Any = None
        for element in self.form_spec.elements:
            if selected_name != element.name:
                continue
            element_visitor = get_visitor(element.parameter_form, self.options)
            disk_value = element_visitor.to_disk(selected_value)
        return selected_name, disk_value
