from datetime import datetime

import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from pydantic import ValidationError


class FollowerRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('FollowerTable')

    def create_follow_request(self, follow_request):
        try:
            # Check if follow request already exists
            existing_request = self.table.scan(
                FilterExpression=Attr('partition_key').eq(
                    f"REQUEST#{follow_request.requester_id}#{follow_request.requestee_id}") & Attr('sort_key').eq(
                    "REQUEST")
            )['Items']

            if existing_request:
                raise BadRequestError("Follow request already exists")

            response = self.table.put_item(
                Item={
                    'partition_key': "REQUEST",
                    'sort_key': f"{follow_request.requester_id}#{follow_request.requestee_id}",
                    'requester_id': follow_request.requester_id,
                    'requestee_id': follow_request.requestee_id,
                    'status': 'pending',
                    'timestamp': follow_request.timestamp.isoformat()
                }
            )
            return response

        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to create follow request DB {e}")

    def accept_follow_request(self, requester_id, requestee_id):
        try:
            self.table.update_item(
                Key={
                    'partition_key': f"REQUEST#{requester_id}#{requestee_id}",
                    'sort_key': "REQUEST"
                },
                UpdateExpression="set #status = :s",
                ExpressionAttributeValues={
                    ':s': 'accepted'
                },
                ExpressionAttributeNames={
                    '#status': 'status'
                }
            )

            # Requester now follows requestee which means that the requester is a follower of the requestee. The
            # relation is uni-directional
            self.table.put_item(
                Item={
                    'partition_key': f"FOLLOWERS",
                    'sort_key': f"{requestee_id}#{requester_id}",
                    'timestamp': datetime.now().isoformat()
                }
            )
            # Store mirrored for efficient queries
            self.table.put_item(
                Item={
                    'partition_key': f"FOLLOWING",
                    'sort_key': f"{requester_id}#{requestee_id}",
                    'timestamp': datetime.now().isoformat()
                }
            )


        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to accept follow request. {e}")

    def deny_follow_request(self, requester_id: str, requestee_id: str):
        try:
            # Update the follow request status to 'rejected'
            response = self.table.update_item(
                Key={
                    'partition_key': f"REQUEST#{requester_id}#{requestee_id}",
                    'sort_key': "REQUEST"
                },
                UpdateExpression="set #status = :s",
                ExpressionAttributeValues={
                    ':s': 'rejected'
                },
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ReturnValues="UPDATED_NEW"
            )
            return response
        except Exception as e:
            print(e)
            raise BadRequestError(f"Unable to deny follow request. {e}")

    def fetch_received_follow_requests(self, user_id: str):
        try:
            response = self.table.query(
                IndexName='RequesteeIDIndex',
                KeyConditionExpression='requestee_id = :requestee_id',
                ExpressionAttributeValues={
                    ':requestee_id': f"{user_id}"
                }
            )
            return response
        except ClientError as e:
            print(e)
            raise BadRequestError(f"Unable to fetch received follow requests. {e}")

    def fetch_sent_follow_requests(self, user_id: str):
        try:
            response = self.table.query(
                IndexName='RequesterIDIndex',
                KeyConditionExpression='requester_id = :requester_id',
                ExpressionAttributeValues={
                    ':requester_id': f"{user_id}"
                }
            )
            return response
        except ClientError as e:
            print(e)
            raise BadRequestError(f"Unable to fetch received follow requests. {e}")

    def get_following(self, user_id: str):
        try:
            following_response = self.table.query(
                KeyConditionExpression=f"partition_key = :following and begins_with(sort_key, '{user_id}')",
                ExpressionAttributeValues={
                    ':following': f"FOLLOWING"
                }
            )
            return following_response.get(['Items'])
        except Exception as e:
            print(e)
            raise BadRequestError(f"Unable to retrieve user connections. {e}")

    def get_followers(self, user_id: str):
        try:
            following_response = self.table.query(
                KeyConditionExpression=f"partition_key = :followers and begins_with(sort_key, '{user_id}')",
                ExpressionAttributeValues={
                    ':followers': f"FOLLOWERS"
                }
            )
            return following_response.get(['Items'])
        except Exception as e:
            print(e)
            raise BadRequestError(f"Unable to retrieve user connections. {e}")
