from typing import List

from pydantic import BaseModel


class UserConnections(BaseModel):
    following: List[str] = []
    followers: List[str] = []
