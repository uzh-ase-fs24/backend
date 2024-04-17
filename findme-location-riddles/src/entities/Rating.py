from pydantic import BaseModel


class Rating(BaseModel):
    user_id: str
    rating: int
