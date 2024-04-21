from typing import List, Optional

from pydantic import BaseModel

from src.entities.User import UserDTO


class UserConnections(BaseModel):
    following: Optional[List[UserDTO]] = []
    followers: Optional[List[UserDTO]] = []


class UserConnectionsIDs(BaseModel):
    following: List[str] = []
    followers: List[str] = []
