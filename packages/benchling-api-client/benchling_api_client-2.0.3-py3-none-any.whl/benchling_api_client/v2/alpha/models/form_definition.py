import datetime
from typing import Any, cast, Dict, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.form_definition_description import FormDefinitionDescription
from ..models.form_definition_version import FormDefinitionVersion
from ..types import UNSET, Unset

T = TypeVar("T", bound="FormDefinition")


@attr.s(auto_attribs=True, repr=False)
class FormDefinition:
    """  """

    _default_version: Union[Unset, FormDefinitionVersion] = UNSET
    _description: Union[Unset, FormDefinitionDescription] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("default_version={}".format(repr(self._default_version)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        return "FormDefinition({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        default_version: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._default_version, Unset):
            default_version = self._default_version.to_dict()

        description: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._description, Unset):
            description = self._description.to_dict()

        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if default_version is not UNSET:
            field_dict["defaultVersion"] = default_version
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_default_version() -> Union[Unset, FormDefinitionVersion]:
            default_version: Union[Unset, FormDefinitionVersion] = UNSET
            _default_version = d.pop("defaultVersion")
            if not isinstance(_default_version, Unset):
                default_version = FormDefinitionVersion.from_dict(_default_version)

            return default_version

        default_version = (
            get_default_version()
            if "defaultVersion" in d
            else cast(Union[Unset, FormDefinitionVersion], UNSET)
        )

        def get_description() -> Union[Unset, FormDefinitionDescription]:
            description: Union[Unset, FormDefinitionDescription] = UNSET
            _description = d.pop("description")
            if not isinstance(_description, Unset):
                description = FormDefinitionDescription.from_dict(_description)

            return description

        description = (
            get_description() if "description" in d else cast(Union[Unset, FormDefinitionDescription], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        form_definition = cls(
            default_version=default_version,
            description=description,
            id=id,
            modified_at=modified_at,
            name=name,
        )

        return form_definition

    @property
    def default_version(self) -> FormDefinitionVersion:
        if isinstance(self._default_version, Unset):
            raise NotPresentError(self, "default_version")
        return self._default_version

    @default_version.setter
    def default_version(self, value: FormDefinitionVersion) -> None:
        self._default_version = value

    @default_version.deleter
    def default_version(self) -> None:
        self._default_version = UNSET

    @property
    def description(self) -> FormDefinitionDescription:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: FormDefinitionDescription) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def modified_at(self) -> datetime.datetime:
        """ Time when the definition was last modified. Will be updated when a new version becomes the default """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
