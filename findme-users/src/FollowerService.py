from datetime import datetime


from src.entities.UserConnections import UserConnectionsIDs
from src.entities.FollowRequest import FollowRequest

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)


class FollowerService:
    def __init__(self, follower_repository):
        self.follower_repository = follower_repository

    def create_follower_request(self, requester_username: str, requester_id: str, requestee_id: str) -> FollowRequest:
        if requester_id == requestee_id:
            raise BadRequestError(
                f"It is not possible to create the follow request since requester ({requester_id}) and requestee ({requestee_id}) are the same person!")

        return self.follower_repository.create_follow_request(
            {
                'requester_username': requester_username,
                'requester_id': requester_id,
                'requestee_id': requestee_id,
                'request_status': 'pending',
                'timestamp': datetime.now()
            }
        )

    def accept_follow_request(self, requester_id: str, requestee_id: str) -> FollowRequest:
        return self.follower_repository.accept_follow_request(requester_id, requestee_id)

    def decline_follow_request(self, requester_id: str, requestee_id: str) -> FollowRequest:
        return self.follower_repository.decline_follow_request(requester_id, requestee_id)

    def get_received_follow_requests(self, user_id: str) -> list[FollowRequest]:
        return self.follower_repository.fetch_received_follow_requests(user_id)

    def get_user_connections(self, user_id: str) -> UserConnectionsIDs:
        return self.follower_repository.get_user_connections(user_id)
