from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.barcode_form_field import BarcodeFormField
from ..models.date_selection_form_field import DateSelectionFormField
from ..models.entity_link_form_field import EntityLinkFormField
from ..models.free_form_text_form_field import FreeFormTextFormField
from ..models.nested_form_field import NestedFormField
from ..models.string_select_form_field import StringSelectFormField
from ..types import UNSET, Unset

T = TypeVar("T", bound="FormDefinitionVersion")


@attr.s(auto_attribs=True, repr=False)
class FormDefinitionVersion:
    """  """

    _definition_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _version_number: Union[Unset, int] = UNSET
    _fields: Union[
        Unset,
        List[
            Union[
                StringSelectFormField,
                FreeFormTextFormField,
                DateSelectionFormField,
                EntityLinkFormField,
                BarcodeFormField,
                NestedFormField,
                UnknownType,
            ]
        ],
    ] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("definition_id={}".format(repr(self._definition_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("version_number={}".format(repr(self._version_number)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FormDefinitionVersion({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        definition_id = self._definition_id
        id = self._id
        version_number = self._version_number
        fields: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = []
            for fields_item_data in self._fields:
                if isinstance(fields_item_data, UnknownType):
                    fields_item = fields_item_data.value
                elif isinstance(fields_item_data, StringSelectFormField):
                    fields_item = fields_item_data.to_dict()

                elif isinstance(fields_item_data, FreeFormTextFormField):
                    fields_item = fields_item_data.to_dict()

                elif isinstance(fields_item_data, DateSelectionFormField):
                    fields_item = fields_item_data.to_dict()

                elif isinstance(fields_item_data, EntityLinkFormField):
                    fields_item = fields_item_data.to_dict()

                elif isinstance(fields_item_data, BarcodeFormField):
                    fields_item = fields_item_data.to_dict()

                else:
                    fields_item = fields_item_data.to_dict()

                fields.append(fields_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if definition_id is not UNSET:
            field_dict["definitionId"] = definition_id
        if id is not UNSET:
            field_dict["id"] = id
        if version_number is not UNSET:
            field_dict["versionNumber"] = version_number
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_definition_id() -> Union[Unset, str]:
            definition_id = d.pop("definitionId")
            return definition_id

        definition_id = get_definition_id() if "definitionId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_version_number() -> Union[Unset, int]:
            version_number = d.pop("versionNumber")
            return version_number

        version_number = get_version_number() if "versionNumber" in d else cast(Union[Unset, int], UNSET)

        def get_fields() -> Union[
            Unset,
            List[
                Union[
                    StringSelectFormField,
                    FreeFormTextFormField,
                    DateSelectionFormField,
                    EntityLinkFormField,
                    BarcodeFormField,
                    NestedFormField,
                    UnknownType,
                ]
            ],
        ]:
            fields = []
            _fields = d.pop("fields")
            for fields_item_data in _fields or []:

                def _parse_fields_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    StringSelectFormField,
                    FreeFormTextFormField,
                    DateSelectionFormField,
                    EntityLinkFormField,
                    BarcodeFormField,
                    NestedFormField,
                    UnknownType,
                ]:
                    fields_item: Union[
                        StringSelectFormField,
                        FreeFormTextFormField,
                        DateSelectionFormField,
                        EntityLinkFormField,
                        BarcodeFormField,
                        NestedFormField,
                        UnknownType,
                    ]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        fields_item = StringSelectFormField.from_dict(data)

                        return fields_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        fields_item = FreeFormTextFormField.from_dict(data)

                        return fields_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        fields_item = DateSelectionFormField.from_dict(data)

                        return fields_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        fields_item = EntityLinkFormField.from_dict(data)

                        return fields_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        fields_item = BarcodeFormField.from_dict(data)

                        return fields_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        fields_item = NestedFormField.from_dict(data)

                        return fields_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                fields_item = _parse_fields_item(fields_item_data)

                fields.append(fields_item)

            return fields

        fields = (
            get_fields()
            if "fields" in d
            else cast(
                Union[
                    Unset,
                    List[
                        Union[
                            StringSelectFormField,
                            FreeFormTextFormField,
                            DateSelectionFormField,
                            EntityLinkFormField,
                            BarcodeFormField,
                            NestedFormField,
                            UnknownType,
                        ]
                    ],
                ],
                UNSET,
            )
        )

        form_definition_version = cls(
            definition_id=definition_id,
            id=id,
            version_number=version_number,
            fields=fields,
        )

        form_definition_version.additional_properties = d
        return form_definition_version

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def definition_id(self) -> str:
        """ API ID of the definition this version belongs to """
        if isinstance(self._definition_id, Unset):
            raise NotPresentError(self, "definition_id")
        return self._definition_id

    @definition_id.setter
    def definition_id(self, value: str) -> None:
        self._definition_id = value

    @definition_id.deleter
    def definition_id(self) -> None:
        self._definition_id = UNSET

    @property
    def id(self) -> str:
        """ API ID of this version """
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
    def version_number(self) -> int:
        """ Number of this version. Monotically increasing starting from 1 """
        if isinstance(self._version_number, Unset):
            raise NotPresentError(self, "version_number")
        return self._version_number

    @version_number.setter
    def version_number(self, value: int) -> None:
        self._version_number = value

    @version_number.deleter
    def version_number(self) -> None:
        self._version_number = UNSET

    @property
    def fields(
        self,
    ) -> List[
        Union[
            StringSelectFormField,
            FreeFormTextFormField,
            DateSelectionFormField,
            EntityLinkFormField,
            BarcodeFormField,
            NestedFormField,
            UnknownType,
        ]
    ]:
        """Each element defines a field in our form. Form fields are composed of a set of attributes at the top level, and a polymorphic set of attributes under the properties attribute. The specific properties that can be passed to a form field are unique to whatever is set in the type attribute. For example, a form field of type STRING_SELECTION will have an attribute within properties of options; however, this options attribute does not make sense for a form field of type ENTITY_LINK."""
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(
        self,
        value: List[
            Union[
                StringSelectFormField,
                FreeFormTextFormField,
                DateSelectionFormField,
                EntityLinkFormField,
                BarcodeFormField,
                NestedFormField,
                UnknownType,
            ]
        ],
    ) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET
