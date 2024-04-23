from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from datetime import datetime

from .entities.FollowRequest import FollowRequest
from .entities.UserConnections import UserConnectionsUsernames


class FollowerService:
    def __init__(self, follower_repository):
        self.follower_repository = follower_repository

    def create_follower_request(self, requester: str, requestee: str) -> FollowRequest:
        if requester == requestee:
            raise BadRequestError(
                "It is not possible to create the follow request since requester and requestee are the same person!"
            )

        return self.follower_repository.create_follow_request(
            {
                "requester": requester,
                "requestee": requestee,
                "request_status": "pending",
                "timestamp": datetime.now(),
            }
        )

    def accept_follow_request(self, requester: str, requestee: str) -> FollowRequest:
        return self.follower_repository.accept_follow_request(requester, requestee)

    def decline_follow_request(self, requester: str, requestee: str) -> FollowRequest:
        return self.follower_repository.decline_follow_request(requester, requestee)

    def get_received_follow_requests(self, username: str) -> list[FollowRequest]:
        return self.follower_repository.fetch_received_follow_requests(username)

    def get_user_connections(self, username: str) -> UserConnectionsUsernames:
        return self.follower_repository.get_user_connections(username)
