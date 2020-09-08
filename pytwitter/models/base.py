from dataclasses import dataclass, Field, MISSING
from typing import (
    Dict,
    Type,
    TypeVar,
)

from dataclasses_json import (
    DataClassJsonMixin,
)

A = TypeVar("A", bound=DataClassJsonMixin)


@dataclass
class BaseModel(DataClassJsonMixin):
    @classmethod
    def new_from_json_dict(cls: Type[A], data: Dict, *, infer_missing=False) -> A:
        """
        Convert json dict to data class
        :param data: A json dict which will convert model class.
        :param infer_missing: if set True, will let missing field (not have default vale) to None
        :return: The data class
        """
        c = cls.from_dict(data, infer_missing=infer_missing)
        # save origin data
        cls._json = data
        return c


def no_compare_field():
    return Field(
        default=None, default_factory=MISSING, init=True,
        repr=False, hash=None, compare=False, metadata=None
    )


def no_repr_field():
    return Field(
        default=None, default_factory=MISSING, init=True,
        repr=False, hash=None, compare=True, metadata=None
    )
