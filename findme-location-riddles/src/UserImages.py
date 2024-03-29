from pydantic import BaseModel


class UserImages(BaseModel):
    user_id: str
    image_ids: list
