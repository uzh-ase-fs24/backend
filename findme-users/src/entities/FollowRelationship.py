from datetime import datetime

from pydantic import BaseModel, Field


class FollowRelationship(BaseModel):
    following: str = Field(..., description="The ID of the user who is following")
    follower: str = Field(..., description="The ID of the user being followed")
    timestamp: datetime = Field(default_factory=datetime.utcnow,
                                description="The timestamp when the follow relationship was established")
