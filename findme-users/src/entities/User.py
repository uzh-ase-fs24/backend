from typing import List, Optional
from pydantic import BaseModel
from src.entities.Score import Score


class User(BaseModel):
    user_id: str
    username: str
    first_name: str
    last_name: str
    scores: List[Score] = []
    average_score: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.scores and isinstance(self.scores[0], Score):
            self.average_score = sum(score.score for score in self.scores) / len(self.scores)

