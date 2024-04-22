from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional
from decimal import Decimal

from src.entities.Rating import Rating
from src.entities.Comment import Comment
from src.entities.Guess import Guess


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

    @field_validator('location')
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValidationError('Coordinate should contain 2 values: latitude and longitude')
        if not (-90 <= v[0] <= 90):
            raise ValidationError('Latitude should be between -90 and 90')
        if not (-180 <= v[1] <= 180):
            raise ValidationError('Longitude should be between -180 and 180')
        return v
