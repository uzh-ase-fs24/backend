import unittest
from unittest.mock import patch
from ..src.entities.FollowRequest import FollowRequest
from moto import mock_aws
import boto3
from aws_lambda_powertools.event_handler.exceptions import BadRequestError
from botocore.exceptions import ClientError
from datetime import datetime
from ..src.FollowerRepository import FollowerRepository


@mock_aws
class TestFollowerRepository(unittest.TestCase):
    def setUp(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.create_table(
            TableName='FollowerTable',
            KeySchema=[
                {'AttributeName': 'partition_key', 'KeyType': 'HASH'},
                {'AttributeName': 'sort_key', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'partition_key', 'AttributeType': 'S'},
                {'AttributeName': 'sort_key', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        self.table.meta.client.get_waiter('table_exists').wait(TableName='FollowerTable')
        self.follower_repository = FollowerRepository()

    def mock_follow_request(self, requester, requestee, status="pending"):
        self.table.put_item(
            Item={
                "partition_key": "REQUEST",
                "sort_key": f"{requester}#{requestee}",
                "requester": requester,
                "requestee": requestee,
                "request_status": status,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def test_create_follow_request_already_exists(self):
        requester = "user1"
        requestee = "user2"
        self.mock_follow_request(requester, requestee)
        with self.assertRaises(BadRequestError):
            self.follower_repository.create_follow_request(
                FollowRequest(requester=requester, requestee=requestee, timestamp=datetime.now(),
                              request_status="pending"))

    def test_create_follow_request_successful(self):
        requester = "user3"
        requestee = "user4"
        follow_request = FollowRequest(requester=requester, requestee=requestee, timestamp=datetime.now(),
                                       request_status="pending")
        result = self.follower_repository.create_follow_request(follow_request)
        self.assertEqual(result.requester, requester)
        self.assertEqual(result.requestee, requestee)

    def test_accept_follow_request_non_existent(self):
        requester = "user1"
        requestee = "user2"
        with self.assertRaises(BadRequestError):
            self.follower_repository.accept_follow_request(requester, requestee)

    def test_accept_follow_request_successful(self):
        requester = "user1"
        requestee = "user2"
        self.mock_follow_request(requester, requestee)
        result = self.follower_repository.accept_follow_request(requester, requestee)
        self.assertEqual(result.request_status, 'accepted')

    def test_decline_follow_request_successful(self):
        requester = "user_exist"
        requestee = "user_exist"
        self.mock_follow_request(requester, requestee, status="pending")
        with patch.object(self.follower_repository, 'does_follow_request_exist', return_value=True):
            with patch.object(self.follower_repository.table, 'update_item',
                              return_value={'Attributes': {'request_status': 'declined', "requester": requester, "requestee":requestee}}):
                result = self.follower_repository.decline_follow_request(requester, requestee)
                self.assertEqual(result.request_status, 'declined')

    def test_fetch_received_follow_requests_no_items(self):
        username = "user_no_request"
        with patch.object(self.follower_repository.table, 'query', return_value={"Items": []}):
            result = self.follower_repository.fetch_received_follow_requests(username)
            self.assertEqual(result, [])

    def test_fetch_sent_follow_requests_no_items(self):
        username = "user_no_request"
        with patch.object(self.follower_repository.table, 'query', return_value={"Items": []}):
            result = self.follower_repository.fetch_sent_follow_requests(username)
            self.assertEqual(result, [])

    def test_does_follow_request_exist_not_exist(self):
        requester = "user_not_exist"
        requestee = "user_not_exist"
        with patch.object(self.follower_repository.table, 'query', return_value={"Items": []}):
            result = self.follower_repository.does_follow_request_exist(requester, requestee)
            self.assertFalse(result)

    def test_get_following_usernames_client_error(self):
        username = "user_error"
        with patch.object(self.follower_repository.table, 'query', side_effect=ClientError({'Error': {}}, 'Query')):
            with self.assertRaises(BadRequestError):
                self.follower_repository._FollowerRepository__get_following_usernames(username)

    def test_get_followers_usernames_client_error(self):
        username = "user_error"
        with patch.object(self.follower_repository.table, 'query', side_effect=ClientError({'Error': {}}, 'Query')):
            with self.assertRaises(BadRequestError):
                self.follower_repository._FollowerRepository__get_followers_usernames(username)

    def test_get_user_connections(self):
        username = "user_connection"
        followers = ['user1', 'user2']
        following = ['user3', 'user4']
        with patch.object(self.follower_repository, '_FollowerRepository__get_followers_usernames',
                          return_value=followers):
            with patch.object(self.follower_repository, '_FollowerRepository__get_following_usernames',
                              return_value=following):
                result = self.follower_repository.get_user_connections(username)
                self.assertEqual(result.followers, followers)
                self.assertEqual(result.following, following)

    def test_create_follow_request_client_error(self):
        requester = "user5"
        requestee = "user6"
        follow_request = FollowRequest(requester=requester, requestee=requestee, timestamp=datetime.now(),
                                       request_status="pending")
        with patch.object(self.follower_repository.table, 'put_item',
                          side_effect=ClientError({'Error': {}}, 'PutItem')):
            with self.assertRaises(BadRequestError):
                self.follower_repository.create_follow_request(follow_request)

    def test_accept_follow_request_client_error(self):
        requester = "user7"
        requestee = "user8"
        self.mock_follow_request(requester, requestee)
        with patch.object(self.follower_repository.table, 'put_item',
                          side_effect=ClientError({'Error': {}}, 'UpdateItem')):
            with self.assertRaises(BadRequestError):
                self.follower_repository.accept_follow_request(requester, requestee)

    def test_decline_follow_request_non_existent(self):
        requester = "user9"
        requestee = "user10"
        with patch.object(self.follower_repository, 'does_follow_request_exist', return_value=False):
            with self.assertRaises(BadRequestError):
                self.follower_repository.decline_follow_request(requester, requestee)

    def test_decline_follow_request_client_error(self):
        requester = "user11"
        requestee = "user12"
        self.mock_follow_request(requester, requestee)
        with patch.object(self.follower_repository.table, 'update_item',
                          side_effect=ClientError({'Error': {}}, 'UpdateItem')):
            with self.assertRaises(BadRequestError):
                self.follower_repository.decline_follow_request(requester, requestee)

    def test_fetch_received_follow_requests_client_error(self):
        username = "user13"
        with patch.object(self.follower_repository.table, 'query', side_effect=ClientError({'Error': {}}, 'Query')):
            with self.assertRaises(BadRequestError):
                self.follower_repository.fetch_received_follow_requests(username)

    def test_fetch_sent_follow_requests_client_error(self):
        username = "user14"
        with patch.object(self.follower_repository.table, 'query', side_effect=ClientError({'Error': {}}, 'Query')):
            with self.assertRaises(BadRequestError):
                self.follower_repository.fetch_sent_follow_requests(username)

    def test_does_follow_request_exist_client_error(self):
        requester = "user15"
        requestee = "user16"
        with patch.object(self.follower_repository.table, 'query', side_effect=ClientError({'Error': {}}, 'Query')):
            with self.assertRaises(BadRequestError):
                self.follower_repository.does_follow_request_exist(requester, requestee)


if __name__ == '__main__':
    unittest.main()
