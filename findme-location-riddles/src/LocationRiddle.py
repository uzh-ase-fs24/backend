from pydantic import BaseModel


class LocationRiddle(BaseModel):
    location_riddle_id: str
    user_id: str
    ratings: list = []
    comments: list = []
    guesses: list = []
