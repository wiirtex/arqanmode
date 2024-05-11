import enum
import typing

import pydantic


class CreateTaskRequest(pydantic.BaseModel):
    data: typing.Dict
    model: str  # name of desired model


class SchemeFieldTypeEnum(enum.StrEnum):
    Integer = 'int'
    String = 'str'
    # after adding new types you need add new lines to validate_model_by_scheme function


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
