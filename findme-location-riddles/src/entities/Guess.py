from pydantic import BaseModel
from .Coordinate import Coordinate


class Guess(BaseModel):
    username: str
    guess: Coordinate

