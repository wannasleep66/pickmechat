from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.aliases import AliasGenerator


class RequestSchema(BaseModel):
    """Базовый класс для запросов"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel),
    )


class ResponseSchema(BaseModel):
    """Базовый класс для ответов"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel)
    )
