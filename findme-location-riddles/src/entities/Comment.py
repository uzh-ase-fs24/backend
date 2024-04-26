from pydantic import BaseModel


class Comment(BaseModel):
    username: str
    comment: str
