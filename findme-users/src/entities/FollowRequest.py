from datetime import datetime

from pydantic import BaseModel, Field


class FollowRequest(BaseModel):
    requester_id: str = Field(..., description="The ID of the user who sent the follow request")
    requestee_id: str = Field(..., description="The ID of the user to whom the follow request was sent")
    status: str = Field(..., description="The status of the follow request, e.g., 'pending', 'accepted', 'rejected'")
    timestamp: datetime = Field(default_factory=datetime.utcnow,
                                description="The timestamp when the follow request was created")
