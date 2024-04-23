from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional

from .Comment import Comment
from .Guess import Guess
from .Rating import Rating


class LocationRiddle(BaseModel):
    location_riddle_id: str
    username: str
    location: List[Decimal]
    ratings: List[Rating] = []
    comments: List[Comment] = []
    guesses: List[Guess] = []
    created_at: int = int(datetime.now().timestamp())
    average_rating: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.ratings and isinstance(self.ratings[0], Rating):
            self.average_rating = sum(rating.rating for rating in self.ratings) / len(
                self.ratings
            )

    @field_validator("location")
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValidationError(
                "Coordinate should contain 2 values: latitude and longitude"
            )
        # ToDo: implement validation for latitude and longitude for coordinates used in frontend
        # if not (-90 <= v[0] <= 90):
        #     raise ValidationError('Latitude should be between -90 and 90')
        # if not (-180 <= v[1] <= 180):
        #     raise ValidationError('Longitude should be between -180 and 180')
        return v

    def to_dto(self, username: str):
        if (
            any(guess.username == username for guess in self.guesses)
            or self.username == username
        ):
            return SolvedLocationRiddleDTO(**self.dict())
        return LocationRiddleDTO(**self.dict())


class SolvedLocationRiddleDTO(BaseModel):
    solved: bool = True
    location_riddle_id: str
    username: str
    location: List[Decimal]
    comments: List[Comment] = []
    guesses: List[Guess] = []
    created_at: int = int(datetime.now().timestamp())
    average_rating: Optional[float] = None
    image_base64: Optional[str] = None

    def __init__(self, **data):
        location_riddle = LocationRiddle(**data)
        super().__init__(
            solved=True,
            location_riddle_id=location_riddle.location_riddle_id,
            username=location_riddle.username,
            location=location_riddle.location,
            comments=location_riddle.comments,
            guesses=location_riddle.guesses,
            created_at=location_riddle.created_at,
            average_rating=location_riddle.average_rating,
        )


class LocationRiddleDTO(BaseModel):
    solved: bool = False
    location_riddle_id: str
    username: str
    comments: List[Comment] = []
    created_at: int = int(datetime.now().timestamp())
    image_base64: Optional[str] = None

    def __init__(self, **data):
        location_riddle = LocationRiddle(**data)
        super().__init__(
            solved=False,
            location_riddle_id=location_riddle.location_riddle_id,
            username=location_riddle.username,
            comments=location_riddle.comments,
            created_at=location_riddle.created_at,
        )
