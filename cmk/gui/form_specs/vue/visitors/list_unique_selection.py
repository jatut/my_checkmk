#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Sequence
from typing import Generic, TypeVar

from cmk.gui.form_specs.private import CascadingSingleChoiceExtended, SingleChoiceExtended
from cmk.gui.form_specs.private.list_unique_selection import (
    ListUniqueSelection,
    UniqueCascadingSingleChoiceElement,
    UniqueSingleChoiceElement,
)
from cmk.gui.form_specs.vue.validators import build_vue_validators
from cmk.gui.i18n import translate_to_current_language

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import CascadingSingleChoice, FormSpec, SingleChoice
from cmk.shared_typing import vue_formspec_components as shared_type_defs

from ._base import FormSpecVisitor
from ._registry import get_visitor
from ._type_defs import DEFAULT_VALUE, DefaultValue, INVALID_VALUE, InvalidValue
from ._utils import (
    compute_validation_errors,
    compute_validators,
    create_validation_error,
    get_title_and_help,
    option_id,
)

T = TypeVar("T")


class ListUniqueSelectionVisitor(Generic[T], FormSpecVisitor[ListUniqueSelection[T], Sequence[T]]):
    def _parse_value(self, raw_value: object) -> Sequence[T] | InvalidValue:
        if isinstance(raw_value, DefaultValue):
            return self.form_spec.prefill.value

        if not isinstance(raw_value, list):
            return INVALID_VALUE
        return raw_value

    def _to_vue(
        self, raw_value: object, parsed_value: Sequence[T] | InvalidValue
    ) -> tuple[shared_type_defs.ListUniqueSelection, list[object]]:
        if isinstance(parsed_value, InvalidValue):
            # TODO: fallback to default message
            parsed_value = []

        title, help_text = get_title_and_help(self.form_spec)

        element_visitor = get_visitor(self._build_element_template(), self.options)
        element_schema, element_vue_default_value = element_visitor.to_vue(DEFAULT_VALUE)

        list_values = []
        for entry in parsed_value:
            # Note: InputHints are not really supported for list elements
            #       We just collect data for a given template
            #       The data cannot be a mixture between values and InputHint
            _spec, element_vue_value = element_visitor.to_vue(entry)
            list_values.append(element_vue_value)

        assert isinstance(
            element_schema, shared_type_defs.SingleChoice | shared_type_defs.CascadingSingleChoice
        )
        return (
            shared_type_defs.ListUniqueSelection(
                title=title,
                help=help_text,
                validators=build_vue_validators(compute_validators(self.form_spec)),
                element_template=element_schema,
                element_default_value=element_vue_default_value,
                add_element_label=self.form_spec.add_element_label.localize(
                    translate_to_current_language
                ),
                remove_element_label=self.form_spec.remove_element_label.localize(
                    translate_to_current_language
                ),
                no_element_label=self.form_spec.no_element_label.localize(
                    translate_to_current_language
                ),
                unique_selection_elements=self._build_unique_selection_elements(),
            ),
            list_values,
        )

    def _build_unique_selection_elements(self) -> list[str]:
        if self.form_spec.single_choice_type is SingleChoice:
            return [
                option_id(element.parameter_form.name)
                for element in self.form_spec.elements
                if element.unique
            ]
        if self.form_spec.single_choice_type is CascadingSingleChoice:
            return [
                element.parameter_form.name for element in self.form_spec.elements if element.unique
            ]
        raise ValueError("Invalid single_choice_type")

    def _build_element_template(self) -> FormSpec[T]:
        if self.form_spec.single_choice_type is SingleChoice:
            return SingleChoiceExtended(
                elements=[
                    element.parameter_form
                    for element in self.form_spec.elements
                    if isinstance(element, UniqueSingleChoiceElement)
                ],
                label=self.form_spec.single_choice_label,
                prefill=self.form_spec.single_choice_prefill,
            )
        if self.form_spec.single_choice_type is CascadingSingleChoice:
            return CascadingSingleChoiceExtended(  # type: ignore[return-value]
                elements=[
                    element.parameter_form
                    for element in self.form_spec.elements
                    if isinstance(element, UniqueCascadingSingleChoiceElement)
                ],
                label=self.form_spec.single_choice_label,
                prefill=self.form_spec.single_choice_prefill,
                layout=self.form_spec.cascading_single_choice_layout,
            )
        raise ValueError("Invalid single_choice_type")

    def _validate(
        self, raw_value: object, parsed_value: Sequence[T] | InvalidValue
    ) -> list[shared_type_defs.ValidationMessage]:
        if isinstance(parsed_value, InvalidValue):
            return create_validation_error(raw_value, Title("Invalid data for list"))

        element_validations = [
            *compute_validation_errors(compute_validators(self.form_spec), parsed_value)
        ]
        element_visitor = get_visitor(self._build_element_template(), self.options)

        for idx, entry in enumerate(parsed_value):
            for validation in element_visitor.validate(entry):
                element_validations.append(
                    shared_type_defs.ValidationMessage(
                        location=[str(idx)] + validation.location,
                        message=validation.message,
                        invalid_value=validation.invalid_value,
                    )
                )
        return element_validations

    def _to_disk(self, raw_value: object, parsed_value: Sequence[T]) -> list[T]:
        disk_values = []
        element_visitor = get_visitor(self._build_element_template(), self.options)
        for entry in parsed_value:
            disk_values.append(element_visitor.to_disk(entry))
        return disk_values
