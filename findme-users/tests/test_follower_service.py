import unittest
from unittest.mock import MagicMock

from ..src.entities.UserConnections import UserConnectionsUsernames
from ..src.FollowerService import FollowerService
from ..src.FollowerRepository import FollowerRepository
from ..src.entities.FollowRequest import FollowRequest
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from datetime import datetime, timedelta


class TestFollowerService(unittest.TestCase):
    def setUp(self):
        self.mock_follower_repository = MagicMock(spec=FollowerRepository)
        self.follower_service = FollowerService(self.mock_follower_repository)
    def test_get_user_connections(self):
        username = "user1"
        expected_connections = UserConnectionsUsernames(usernames=["user2", "user3"])
        self.mock_follower_repository.get_user_connections.return_value = expected_connections
        result = self.follower_service.get_user_connections(username)
        self.assertEqual(result, expected_connections)
        self.mock_follower_repository.get_user_connections.assert_called_once_with(username)

    def test_create_follower_request_same_user(self):
        requester = "user1"
        requestee = "user1"
        with self.assertRaises(BadRequestError):
            self.follower_service.create_follower_request(requester, requestee)

    def test_create_follower_request_valid(self):
        requester = "user1"
        requestee = "user2"

        follow_request = FollowRequest(requester=requester, requestee=requestee,
                                       request_status="pending", timestamp=datetime.now())
        self.mock_follower_repository.create_follow_request.return_value = follow_request
        result = self.follower_service.create_follower_request(requester, requestee)

        self.assertEqual(result.request_status, follow_request.request_status)
        self.assertEqual(result.requester, follow_request.requester)
        self.assertEqual(result.requestee, follow_request.requestee)
        self.assertAlmostEqual(result.timestamp, follow_request.timestamp, delta=timedelta(seconds=1))

    def test_accept_follow_request(self):
        requester = "user1"
        requestee = "user2"
        expected_response = FollowRequest(requester=requester, requestee=requestee, request_status="accepted",
                                          timestamp=datetime.now())
        self.mock_follower_repository.accept_follow_request.return_value = expected_response
        result = self.follower_service.accept_follow_request(requester, requestee)
        self.assertEqual(result, expected_response)
        self.mock_follower_repository.accept_follow_request.assert_called_once_with(requester, requestee)

    def test_decline_follow_request(self):
        requester = "user1"
        requestee = "user2"
        expected_response = FollowRequest(requester=requester, requestee=requestee, request_status="declined",
                                          timestamp=datetime.now())
        self.mock_follower_repository.decline_follow_request.return_value = expected_response
        result = self.follower_service.decline_follow_request(requester, requestee)
        self.assertEqual(result, expected_response)
        self.mock_follower_repository.decline_follow_request.assert_called_once_with(requester, requestee)

    def test_get_received_follow_requests(self):
        username = "user2"
        expected_requests = [
            FollowRequest(requester="user1", requestee=username, request_status="pending", timestamp=datetime.now()),
            FollowRequest(requester="user3", requestee=username, request_status="pending", timestamp=datetime.now())
        ]
        self.mock_follower_repository.fetch_received_follow_requests.return_value = expected_requests
        result = self.follower_service.get_received_follow_requests(username)
        self.assertEqual(result, expected_requests)
        self.mock_follower_repository.fetch_received_follow_requests.assert_called_once_with(username)



if __name__ == "__main__":
    unittest.main()
