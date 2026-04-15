from typing import Optional, Type, Dict, List, get_origin, Union, get_args
from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.fields import FieldInfo

T = TypeVar("T")



def _get_wrapped_type(tp):
    origin = get_origin(tp)
    if origin is Union:
        args = get_args(tp)
        if len(args) == 2 and type(None) in args:
            return args[0] if args[1] is type(None) else args[1]
    return tp


def extra_filter_fields(**extensions):
    """
    Supported extra fields:
    in_: value in list  (for relations)
    not_in: value not in list   (for relations)
    gt: greater than
    ge: greater than or equal
    lt: less than
    le: less than or equal
    is_null: value is null  (for nullable fields)
    is_not_null: value is not null  (for nullable fields (just in case))
    like: entry filter
    """

    def decorator(cls: Type[BaseModel]) -> Type[BaseModel]:
        new_fields: Dict[str, FieldInfo] = {}
        new_annotations: Dict[str, Optional[type]] = {}
        for ext_type, fields in extensions.items():
            for field_name in fields:
                cleaned_ext_type = ext_type.strip("_")
                ext_field_name = f"{field_name}__{cleaned_ext_type}"
                if ext_field_name not in cls.model_fields:
                    original_type = _get_wrapped_type(cls.model_fields[field_name].annotation)
                    if cleaned_ext_type in ["in", "not_in"]:
                        ext_type_annotation = Optional[List[original_type]]
                    elif cleaned_ext_type in ["is_null", "is_not_null"]:
                        ext_type_annotation = Optional[bool]
                    else:
                        ext_type_annotation = Optional[original_type]
                    if cleaned_ext_type == "like":
                        if not original_type is str:
                            raise TypeError('Attribute with "like" extension can be str only')
                    new_annotations[ext_field_name] = ext_type_annotation
                    new_fields[ext_field_name] = FieldInfo(
                        default=Query(default=None),
                        annotation=ext_type_annotation,
                        description=f"{cleaned_ext_type.upper()} for {field_name}",
                    )

        cls.model_fields.update(new_fields)
        cls.__annotations__.update(new_annotations)
        cls.model_rebuild(force=True)

        return cls

    return decorator



class PaginationRequest(BaseModel):
    limit: int = 50
    offset: int = 0
    order_by: str = "id"
    sorting: str = "asc"

    @property
    def is_desc(self):
        return self.sorting == "desc"


class PaginationResultSchema[T](BaseModel):
    items: tuple[T]
    total: int
    limit: int
    offset: int
    order_by: str = "id"
    sorting: str = "asc"
