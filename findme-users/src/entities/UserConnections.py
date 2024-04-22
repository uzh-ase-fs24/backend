from pydantic import BaseModel
from typing import List, Optional

from .User import UserDTO


class UserConnections(BaseModel):
    following: Optional[List[UserDTO]] = []
    followers: Optional[List[UserDTO]] = []


class UserConnectionsIDs(BaseModel):
    following: List[str] = []
    followers: List[str] = []
