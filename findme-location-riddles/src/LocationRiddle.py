from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class Rating(BaseModel):
    user_id: str
    rating: int


class Comment(BaseModel):
    user_id: str
    comment: str


class Guess(BaseModel):
    user_id: str
    guess: List[Decimal]


class LocationRiddle(BaseModel):
    location_riddle_id: str
    user_id: str
    location: List[Decimal]
    ratings: List[Rating] = []
    comments: List[Comment] = []
    guesses: List[Guess] = []
    created_at: int = int(datetime.now().timestamp())
    average_rating: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.ratings and isinstance(self.ratings[0], Rating):
            self.average_rating = sum(rating.rating for rating in self.ratings) / len(self.ratings)
