from datetime import datetime

from pydantic import BaseModel, Field


class FollowRequest(BaseModel):
    requester: str = Field(
        description="The username of the user who sent the follow request"
    )
    requestee: str = Field(
        description="The username of the user to whom the follow request was sent"
    )
    request_status: str = Field(
        description="The status of the follow request, e.g., 'pending', 'accepted', 'rejected'"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="The timestamp when the follow request was created",
    )
