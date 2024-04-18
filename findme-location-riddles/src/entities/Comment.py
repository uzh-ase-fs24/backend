from pydantic import BaseModel


class Comment(BaseModel):
    user_id: str
    comment: str
