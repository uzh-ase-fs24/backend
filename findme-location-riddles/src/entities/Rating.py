from pydantic import BaseModel, Field


class Rating(BaseModel):
    user_id: str
    rating: int = Field(..., ge=1, le=5)
