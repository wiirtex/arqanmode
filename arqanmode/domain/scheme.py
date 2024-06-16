import typing
from enum import Enum

import pydantic


class SchemeFieldTypeEnum(Enum):
    Integer = "integer"
    String = "string"


class CreateTaskRequest(pydantic.BaseModel):
    data: typing.Dict
    model: str  # name of desired model


class SchemeFieldV1(pydantic.BaseModel):
    name: str
    value: SchemeFieldTypeEnum


class SchemeV1(pydantic.BaseModel):
    name: str
    fields: pydantic.conlist(SchemeFieldV1, min_length=1)


class ModelV1(pydantic.BaseModel):
    model_name: str
    scheme: SchemeV1

    @classmethod
    @pydantic.model_validator(mode='before')
    def check_not_none(cls, data):
        if isinstance(data, dict):
            assert ('scheme' in data), "field scheme must not be omitted"
        return data
