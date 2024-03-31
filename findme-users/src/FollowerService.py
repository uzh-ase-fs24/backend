from datetime import datetime
from typing import List

from pydantic import parse_obj_as
from src.FollowerRepository import FollowerRepository
from src.entities.FollowRequest import FollowRequest
from src.entities.UserConnections import UserConnections

from src.entities.FollowRelationship import FollowRelationship


class FollowerService:
    def __init__(self):
        self.follower_repository = FollowerRepository()

    def create_follower_request(self, requester_id, requestee_id):
        follow_request = FollowRequest(
            requester_id=requester_id,
            requestee_id=requestee_id,
            status='pending',
            timestamp=datetime.now()
        )

        self.follower_repository.create_follow_request(follow_request)

        return follow_request

    def accept_follow_request(self, requester_id, requestee_id):
        self.follower_repository.accept_follow_request(requester_id, requestee_id)
        return f"Follow request by {requester_id} accepted!"

    def deny_follow_request(self, requester_id, requestee_id):
        response = self.follower_repository.deny_follow_request(requester_id, requestee_id)
        update_follow_request = FollowRequest(**response['items'])
        return update_follow_request

    def get_received_follow_requests(self, user_id):
        response = self.follower_repository.fetch_received_follow_requests(user_id)
        follow_requests = parse_obj_as(List[FollowRequest], response['Items'])
        return follow_requests

    def get_user_connections(self, user_id):
        following_response = self.follower_repository.get_following(user_id)
        followers_response = self.follower_repository.get_followers(user_id)

        connections = UserConnections()

        # Always take the second user_id since the first is indicating who we are searching for
        connections.following = [item['sort_key'].split("#")[1] for item in following_response['Items']]
        connections.followers = [item['sort_key'].split("#")[1] for item in followers_response['Items']]

        return connections
