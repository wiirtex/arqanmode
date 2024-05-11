import typing

from arqanmode import SchemeV1, SchemeFieldTypeEnum


class ValidationError(Exception):
    """ raised when the input is incorrect"""

    class FieldError:
        field: str
        error: str

    errors: typing.Dict[str, str]

    def __init__(self, errors: typing.List[FieldError]):
        self.errors = errors
        super().__init__(f"errors: {errors}")


def validate_model_by_scheme(scheme: SchemeV1, data: typing.Dict):
    field_type_by_name = {}
    for field in scheme.fields:
        field_type_by_name[field.name] = field.value

    if "name" not in data:
        raise ValidationError({
            "name": "is not specified"
        })
    if "fields" not in data:
        raise ValidationError({
            "fields": "is not specified"
        })

    name = scheme.name
    if name != data["name"]:
        raise ValidationError({
            "name": "schema name is not supported"
        })

    for field in data["fields"]:
        field_name = field["name"]
        if field_name not in field_type_by_name:
            raise ValidationError({
                field_name: "unexpected field"
            })

        field_value = field["value"]
        if field_type_by_name[field_name] == SchemeFieldTypeEnum.Integer:
            if not isinstance(field_value, int):
                raise ValidationError({
                    field_name: "type is not expected"
                })
        elif field_type_by_name[field_name] == SchemeFieldTypeEnum.String:
            if not isinstance(field_value, str):
                raise ValidationError({
                    field_name: "type is not expected"
                })

        del field_type_by_name[field_name]

    if len(field_type_by_name) != 0:
        errors = {}
        for name in field_type_by_name:
            errors[name] = "field is not filled"
        raise ValidationError(errors)
