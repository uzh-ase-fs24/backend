from datetime import datetime
from typing import List

from pydantic import parse_obj_as
from src.entities.FollowRequest import FollowRequest

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)



class FollowerService:
    def __init__(self, follower_repository):
        self.follower_repository = follower_repository

    def create_follower_request(self, requester_username, requester_id, requestee_id):
        if requester_id == requestee_id:
            raise BadRequestError(
                f"It is not possible to create the follow request since requester ({requester_id}) and requestee ({requestee_id}) are the same person!")

        follow_request = FollowRequest(
            requester_username=requester_username,
            requester_id=requester_id,
            requestee_id=requestee_id,
            request_status='pending',
            timestamp=datetime.now()
        )

        self.follower_repository.create_follow_request(follow_request)

        return follow_request

    def accept_follow_request(self, requester_id, requestee_id):
        if self.follower_repository.does_follow_request_exist(requester_id, requestee_id):
            self.follower_repository.accept_follow_request(requester_id, requestee_id)
            return { "result": f"Follow request by {requester_id} accepted!"}
        else:
            raise BadRequestError(f"The given follow request does not exist!")

    def deny_follow_request(self, requester_id, requestee_id):
        if self.follower_repository.does_follow_request_exist(requester_id, requestee_id):
            self.follower_repository.deny_follow_request(requester_id, requestee_id)
            return { "result": f"Follow request by {requester_id} declined!"}
        else:
            raise BadRequestError(f"The given follow request does not exist!")

    def get_received_follow_requests(self, user_id):
        response = self.follower_repository.fetch_received_follow_requests(user_id)
        follow_requests = parse_obj_as(List[FollowRequest], response['Items'])

        return follow_requests

    def get_user_connections(self, user_id):
        following_response = self.follower_repository.get_following(user_id)
        followers_response = self.follower_repository.get_followers(user_id)

        # Always take the second user_id since the first is indicating who we are searching for
        following = [item['sort_key'].split("#")[1] for item in following_response['Items']]
        followers = [item['sort_key'].split("#")[1] for item in followers_response['Items']]

        return {'following': following, 'followers': followers}

