from pydantic import BaseModel


class Score(BaseModel):
    location_riddle_id: str
    score: int
