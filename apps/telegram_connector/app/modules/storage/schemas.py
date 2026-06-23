from pydantic import BaseModel


class StreamingResponse(BaseModel):
    content: bytes
    content_type: str
