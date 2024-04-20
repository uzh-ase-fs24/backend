from datetime import datetime

import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from pydantic import ValidationError

from src.entities.FollowRequest import FollowRequest
from src.entities.UserConnections import UserConnectionsIDs
from src.base.AbstractFollowerRepository import AbstractFollowerRepository


class FollowerRepository(AbstractFollowerRepository):
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('FollowerTable')

    def create_follow_request(self, follow_request_data: dict) -> FollowRequest:
        try:
            follow_request = FollowRequest(**follow_request_data)
        except ValidationError as e:
            print(f"unable to create follow request with provided parameters. {e}")
            raise BadRequestError(f"unable to create follow request with provided parameters. {e}")

        # Check if follow request already exists
        existing_request = self.table.scan(
            FilterExpression=Attr('partition_key').eq(
                f"REQUEST") & Attr('sort_key').eq(
                f"{follow_request.requester_id}#{follow_request.requestee_id}")
        )['Items']

        if existing_request:
            raise BadRequestError("Follow request already exists")

        try:
            self.table.put_item(
                Item={
                    'partition_key': "REQUEST",
                    'sort_key': f"{follow_request.requester_id}#{follow_request.requestee_id}",
                    'requester_id': follow_request.requester_id,
                    'requestee_id': follow_request.requestee_id,
                    'requester_username': follow_request.requester_username,
                    'request_status': 'pending',
                    'timestamp': follow_request.timestamp.isoformat()
                },
            )
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

        return follow_request

    def accept_follow_request(self, requester_id: str, requestee_id: str) -> FollowRequest:
        if not self.does_follow_request_exist(requester_id, requestee_id):
            raise BadRequestError(f"The follow request from user ${requester_id} does not exist!")

        try:
            response = self.table.update_item(
                Key={
                    'partition_key': f"REQUEST",
                    'sort_key': f"{requester_id}#{requestee_id}"
                },
                UpdateExpression="SET request_status = :s",
                ExpressionAttributeValues={
                    ':s': 'accepted'
                },
                ReturnValues="ALL_NEW"
            )

            # relation is uni-directional
            # sort_key: "requestee" has the follower "requester"
            self.table.put_item(
                Item={
                    'partition_key': f"FOLLOWERS",
                    'sort_key': f"{requestee_id}#{requester_id}",
                    'timestamp': datetime.now().isoformat(),
                }
            )

            # Store mirrored for efficient queries
            # sort_key: "requester" is following "requestee"
            self.table.put_item(
                Item={
                    'partition_key': f"FOLLOWING",
                    'sort_key': f"{requester_id}#{requestee_id}",
                    'timestamp': datetime.now().isoformat(),
                }
            )
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

        return FollowRequest(**response['Attributes'])

    def decline_follow_request(self, requester_id: str, requestee_id: str) -> FollowRequest:
        if not self.does_follow_request_exist(requester_id, requestee_id):
            raise BadRequestError(f"The follow request from user ${requester_id} does not exist!")

        try:
            # Update the follow request status to 'declined'
            response = self.table.update_item(
                Key={
                    'partition_key': f"REQUEST",
                    'sort_key': f"{requester_id}#{requestee_id}"
                },
                UpdateExpression="set request_status = :s",
                ExpressionAttributeValues={
                    ':s': 'declined'
                },
                ReturnValues="UPDATED_NEW"
            )
        except Exception as e:
            print(f"Unable to deny follow request. {e}")
            raise BadRequestError(f"Unable to deny follow request. {e}")

        return FollowRequest(**response['Attributes'])

    def fetch_received_follow_requests(self, user_id: str) -> list[FollowRequest]:
        try:
            response = self.table.query(
                IndexName='RequesteeIDIndex',
                KeyConditionExpression='requestee_id = :requestee_id AND partition_key = :partition_key',
                FilterExpression='request_status = :status_val',
                ExpressionAttributeValues={
                    ':requestee_id': f"{user_id}",
                    ':status_val': "pending",
                    ':partition_key': "REQUEST"
                },
            )
        except ClientError as e:
            print(f"Unable to fetch received follow requests. {e}")
            raise BadRequestError(f"Unable to fetch received follow requests. {e}")

        return [FollowRequest(**item) for item in response['Items']]

    def fetch_sent_follow_requests(self, user_id: str) -> list[FollowRequest]:
        try:
            response = self.table.query(
                IndexName='RequesterIDIndex',
                KeyConditionExpression='requester_id = :requester_id',
                ExpressionAttributeValues={
                    ':requester_id': f"{user_id}"
                }
            )
        except ClientError as e:
            print(f"Unable to fetch received follow requests. {e}")
            raise BadRequestError(f"Unable to fetch received follow requests. {e}")

        return [FollowRequest(**item) for item in response['Items']]

    def does_follow_request_exist(self, requester_id: str, requestee_id: str) -> bool:
        follow_request_id = f"{requester_id}#{requestee_id}"
        try:
            follow_request = self.table.query(
                KeyConditionExpression="partition_key = :partition_key AND sort_key = :user_id",
                ExpressionAttributeValues={
                    ':partition_key': "REQUEST",
                    ':user_id': follow_request_id
                }
            )
        except ClientError as e:
            print(f"Couldn't fetch follow request. {e}")
            raise BadRequestError(f"Couldn't fetch follow request. {e}")

        return 'Items' in follow_request and len(follow_request['Items']) == 1 and follow_request['Items'][0][
            'request_status'] == 'pending'

    def __get_following_ids(self, user_id: str) -> list[int]:
        try:
            following_response = self.table.query(
                KeyConditionExpression="partition_key = :partition_key AND begins_with(sort_key, :user_id)",
                ExpressionAttributeValues={
                    ':partition_key': "FOLLOWING",
                    ':user_id': user_id
                }
            )
        except ClientError as e:
            print(f"Unable to retrieve user connections. {e}")
            raise BadRequestError(f"Unable to retrieve user connections. {e}")
        return [item['sort_key'].split("#")[1] for item in following_response['Items']]

    def __get_followers_ids(self, user_id: str) -> list[int]:
        try:
            follower_response = self.table.query(
                KeyConditionExpression="partition_key = :partition_key AND begins_with(sort_key, :user_id)",
                ExpressionAttributeValues={
                    ':partition_key': "FOLLOWERS",
                    ':user_id': user_id
                }
            )
        except ClientError as e:
            print(f"Unable to retrieve user connections. {e}")
            raise BadRequestError(f"Unable to retrieve user connections. {e}")
        return [item['sort_key'].split("#")[1] for item in follower_response['Items']]

    def get_user_connections(self, user_id: str) -> UserConnectionsIDs:
        return UserConnectionsIDs(
            **{'followers': self.__get_followers_ids(user_id),
               'following': self.__get_following_ids(user_id)}
        )
