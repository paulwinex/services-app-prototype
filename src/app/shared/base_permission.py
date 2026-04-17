from enum import StrEnum
from typing import TypeVar, Self

# T = TypeVar("T", bound="PermissionsBase")


class PermissionsBase(StrEnum):
    """Base permissions enum for identity domain."""

    def __new__(cls, value: str) -> Self:
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init_subclass__(cls, *, prefix: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._scope_prefix_ = prefix or cls.__name__.lower().replace("permission", "")

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    @property
    def value(self) -> str:
        raw = super().value
        if prefix := getattr(self.__class__, "_scope_prefix_", None):
            return f"{prefix}.{raw}"
        return raw

    @classmethod
    def get_list(cls) -> list[str]:
        return list(map(str, cls))

    @classmethod
    def get_all_permissions(cls: type[T]) -> list[T]:
        """Get all permission instances from this class."""
        return list(cls)
