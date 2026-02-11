from pydantic import BaseModel


class UserSchema(BaseModel):
    external_id: str
    name: str | None = None
    avatar_url: str | None = None
