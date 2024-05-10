from datetime import datetime

import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from .entities.PartitionKey import PartitionKey
from .base.AbstractFollowerRepository import AbstractFollowerRepository
from .entities.FollowRequest import FollowRequest
from .entities.UserConnections import UserConnectionsUsernames

logger = Logger()


class FollowerRepository(AbstractFollowerRepository):
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-central-2")
        self.table = self.dynamodb.Table("FollowerTable")

    def create_follow_request(self, follow_request: FollowRequest) -> FollowRequest:
        # Check if follow request already exists
        existing_request = self.table.scan(
            FilterExpression=Attr("partition_key").eq(PartitionKey.REQUEST.value)
            & Attr("sort_key").eq(
                f"{follow_request.requester}#{follow_request.requestee}"
            )
        )["Items"]
        if existing_request:
            raise BadRequestError("Follow request already exists")

        try:
            self.table.put_item(
                Item={
                    "partition_key": PartitionKey.REQUEST.value,
                    "sort_key": f"{follow_request.requester}#{follow_request.requestee}",
                    "requester": follow_request.requester,
                    "requestee": follow_request.requestee,
                    "request_status": "pending",
                    "timestamp": follow_request.timestamp.isoformat(),
                },
            )
        except ClientError as e:
            logger.error(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

        return follow_request

    def accept_follow_request(self, requester: str, requestee: str) -> FollowRequest:
        if not self.does_follow_request_exist(requester, requestee):
            raise BadRequestError(
                f"The follow request from user ${requester} does not exist!"
            )

        try:
            response = self.table.update_item(
                Key={
                    "partition_key": PartitionKey.REQUEST.value,
                    "sort_key": f"{requester}#{requestee}",
                },
                UpdateExpression="SET request_status = :s",
                ExpressionAttributeValues={":s": "accepted"},
                ReturnValues="ALL_NEW",
            )

            # relation is uni-directional
            # sort_key: "requestee" has the follower "requester"
            self.table.put_item(
                Item={
                    "partition_key": PartitionKey.FOLLOWERS.value,
                    "sort_key": f"{requestee}#{requester}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Store mirrored for efficient queries
            # sort_key: "requester" is following "requestee"
            self.table.put_item(
                Item={
                    "partition_key": PartitionKey.FOLLOWING.value,
                    "sort_key": f"{requester}#{requestee}",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        except ClientError as e:
            logger.error(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

        return FollowRequest(**response["Attributes"])

    def decline_follow_request(self, requester: str, requestee: str) -> FollowRequest:
        if not self.does_follow_request_exist(requester, requestee):
            raise BadRequestError(
                f"The follow request from user ${requester} does not exist!"
            )

        try:
            # Update the follow request status to 'declined'
            response = self.table.update_item(
                Key={
                    "partition_key": PartitionKey.REQUEST.value,
                    "sort_key": f"{requester}#{requestee}",
                },
                UpdateExpression="SET request_status = :s",
                ExpressionAttributeValues={":s": "declined"},
                ReturnValues="ALL_NEW",
            )
        except Exception as e:
            logger.error(f"Unable to deny follow request. {e}")
            raise BadRequestError(f"Unable to deny follow request. {e}")

        return FollowRequest(**response["Attributes"])

    def fetch_received_follow_requests(self, username: str) -> list[FollowRequest]:
        try:
            response = self.table.query(
                IndexName="RequesteeIndex",
                KeyConditionExpression="requestee = :requestee AND partition_key = :partition_key",
                FilterExpression="request_status = :status_val",
                ExpressionAttributeValues={
                    ":requestee": username,
                    ":status_val": "pending",
                    ":partition_key": PartitionKey.REQUEST.value,
                },
            )
        except ClientError as e:
            logger.error(f"Unable to fetch received follow requests. {e}")
            raise BadRequestError(f"Unable to fetch received follow requests. {e}")

        return [FollowRequest(**item) for item in response["Items"]]

    def fetch_sent_follow_requests(self, username: str) -> list[FollowRequest]:
        try:
            response = self.table.query(
                IndexName="RequesterIndex",
                KeyConditionExpression="requester = :requester",
                ExpressionAttributeValues={":requester": username},
            )
        except ClientError as e:
            logger.error(f"Unable to fetch received follow requests. {e}")
            raise BadRequestError(f"Unable to fetch received follow requests. {e}")

        return [FollowRequest(**item) for item in response["Items"]]

    def does_follow_request_exist(self, requester: str, requestee: str) -> bool:
        follow_request_id = f"{requester}#{requestee}"
        try:
            follow_request = self.table.query(
                KeyConditionExpression="partition_key = :partition_key AND sort_key = :follow_request_id",
                ExpressionAttributeValues={
                    ":partition_key": PartitionKey.REQUEST.value,
                    ":follow_request_id": follow_request_id,
                },
            )
        except ClientError as e:
            logger.error(f"Couldn't fetch follow request. {e}")
            raise BadRequestError(f"Couldn't fetch follow request. {e}")

        return (
            "Items" in follow_request
            and len(follow_request["Items"]) == 1
            and follow_request["Items"][0]["request_status"] == "pending"
        )

    def __get_following_usernames(self, username: str) -> list[int]:
        try:
            following_response = self.table.query(
                KeyConditionExpression="partition_key = :partition_key AND begins_with(sort_key, :username)",
                ExpressionAttributeValues={
                    ":partition_key": PartitionKey.FOLLOWING.value,
                    ":username": username,
                },
            )
        except ClientError as e:
            logger.error(f"Unable to retrieve user connections. {e}")
            raise BadRequestError(f"Unable to retrieve user connections. {e}")
        return [item["sort_key"].split("#")[1] for item in following_response["Items"]]

    def __get_followers_usernames(self, username: str) -> list[str]:
        try:
            follower_response = self.table.query(
                KeyConditionExpression="partition_key = :partition_key AND begins_with(sort_key, :username)",
                ExpressionAttributeValues={
                    ":partition_key": PartitionKey.FOLLOWERS.value,
                    ":username": username,
                },
            )
        except ClientError as e:
            logger.error(f"Unable to retrieve user connections. {e}")
            raise BadRequestError(f"Unable to retrieve user connections. {e}")
        return [item["sort_key"].split("#")[1] for item in follower_response["Items"]]

    def get_user_connections(self, username: str) -> UserConnectionsUsernames:
        return UserConnectionsUsernames(
            **{
                "followers": self.__get_followers_usernames(username),
                "following": self.__get_following_usernames(username),
            }
        )
