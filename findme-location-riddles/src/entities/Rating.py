from pydantic import BaseModel, Field


class Rating(BaseModel):
    username: str
    rating: int = Field(..., ge=1, le=5)
