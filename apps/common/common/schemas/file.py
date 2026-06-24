from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FileSchema(BaseModel):
    id: int
    filename: str
    path: str
    content_type: str
    size: int

    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=to_camel))
