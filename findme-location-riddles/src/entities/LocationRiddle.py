from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional

from .Coordinate import Coordinate
from .Comment import Comment
from .Guess import Guess
from .Rating import Rating


class LocationRiddle(BaseModel):
    location_riddle_id: str
    username: str
    location: Coordinate
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
    location: Coordinate
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
    average_rating: Optional[float] = None
    image_base64: Optional[str] = None

    def __init__(self, **data):
        location_riddle = LocationRiddle(**data)
        super().__init__(
            solved=False,
            location_riddle_id=location_riddle.location_riddle_id,
            username=location_riddle.username,
            comments=location_riddle.comments,
            created_at=location_riddle.created_at,
            average_rating=location_riddle.average_rating,
        )
