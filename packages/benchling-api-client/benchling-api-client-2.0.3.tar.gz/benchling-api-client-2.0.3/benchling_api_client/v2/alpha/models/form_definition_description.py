from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="FormDefinitionDescription")


@attr.s(auto_attribs=True, repr=False)
class FormDefinitionDescription:
    """  """

    _text: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("text={}".format(repr(self._text)))
        return "FormDefinitionDescription({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        text = self._text

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_text() -> Union[Unset, str]:
            text = d.pop("text")
            return text

        text = get_text() if "text" in d else cast(Union[Unset, str], UNSET)

        form_definition_description = cls(
            text=text,
        )

        return form_definition_description

    @property
    def text(self) -> str:
        if isinstance(self._text, Unset):
            raise NotPresentError(self, "text")
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @text.deleter
    def text(self) -> None:
        self._text = UNSET
