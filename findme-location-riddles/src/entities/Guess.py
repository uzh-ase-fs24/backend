from pydantic import BaseModel
from typing import List
from decimal import Decimal


class Guess(BaseModel):
    user_id: str
    guess: List[Decimal]
