from typing import List

from pydantic import BaseModel

from src.entities.User import User


class UserConnections(BaseModel):
    following: List[User] = []
    followers: List[User] = []


class UserConnectionsIDs(BaseModel):
    following: List[str] = []
    followers: List[str] = []
