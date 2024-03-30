from datetime import datetime

from pydantic import BaseModel


class LocationRiddle(BaseModel):
    location_riddle_id: str
    user_id: str
    ratings: list = []
    comments: list = []
    guesses: list = []
    created_at: int = int(datetime.now().timestamp())
