from pydantic import BaseModel
from typing import List, Optional

from .Score import Score


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    scores: List[Score] = []
    average_score: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.scores and isinstance(self.scores[0], Score):
            self.average_score = sum(score.score for score in self.scores) / len(
                self.scores
            )

    def to_dto(self):
        return UserDTO(**self.dict())


class UserDTO(BaseModel):
    username: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    average_score: Optional[float] = None

    def __init__(self, **data):
        user = User(**data)
        super().__init__(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            bio=user.bio,
            average_score=user.average_score,
        )


class UserPostDTO(BaseModel):
    first_name: str
    last_name: str
    bio: Optional[str] = None


class UserPutDTO(BaseModel):
    first_name: str
    last_name: str
    bio: Optional[str] = None
