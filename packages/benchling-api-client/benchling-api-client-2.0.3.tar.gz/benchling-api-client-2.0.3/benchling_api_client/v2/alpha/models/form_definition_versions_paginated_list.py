from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.form_definition_version import FormDefinitionVersion
from ..types import UNSET, Unset

T = TypeVar("T", bound="FormDefinitionVersionsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class FormDefinitionVersionsPaginatedList:
    """  """

    _form_definition_versions: Union[Unset, List[FormDefinitionVersion]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("form_definition_versions={}".format(repr(self._form_definition_versions)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "FormDefinitionVersionsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        form_definition_versions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._form_definition_versions, Unset):
            form_definition_versions = []
            for form_definition_versions_item_data in self._form_definition_versions:
                form_definition_versions_item = form_definition_versions_item_data.to_dict()

                form_definition_versions.append(form_definition_versions_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if form_definition_versions is not UNSET:
            field_dict["formDefinitionVersions"] = form_definition_versions
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_form_definition_versions() -> Union[Unset, List[FormDefinitionVersion]]:
            form_definition_versions = []
            _form_definition_versions = d.pop("formDefinitionVersions")
            for form_definition_versions_item_data in _form_definition_versions or []:
                form_definition_versions_item = FormDefinitionVersion.from_dict(
                    form_definition_versions_item_data
                )

                form_definition_versions.append(form_definition_versions_item)

            return form_definition_versions

        form_definition_versions = (
            get_form_definition_versions()
            if "formDefinitionVersions" in d
            else cast(Union[Unset, List[FormDefinitionVersion]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        form_definition_versions_paginated_list = cls(
            form_definition_versions=form_definition_versions,
            next_token=next_token,
        )

        return form_definition_versions_paginated_list

    @property
    def form_definition_versions(self) -> List[FormDefinitionVersion]:
        if isinstance(self._form_definition_versions, Unset):
            raise NotPresentError(self, "form_definition_versions")
        return self._form_definition_versions

    @form_definition_versions.setter
    def form_definition_versions(self, value: List[FormDefinitionVersion]) -> None:
        self._form_definition_versions = value

    @form_definition_versions.deleter
    def form_definition_versions(self) -> None:
        self._form_definition_versions = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
