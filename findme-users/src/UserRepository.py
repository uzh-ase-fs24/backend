import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pydantic import ValidationError

from .base.AbstractUserRepository import AbstractUserRepository
from .entities.Score import Score
from .entities.User import User, UserPutDTO


class UserRepository(AbstractUserRepository):
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-central-2")
        self.table = self.dynamodb.Table("usersTable")

    def post_user_to_db(self, user: User) -> User:
        if self.does_user_with_username_exist(user.username):
            raise BadRequestError(
                f"User with username '{user.username}' already has an account!"
            )

        return self.__put_user_to_db(user)

    def update_user_in_db(self, username: str, user_data: UserPutDTO) -> User:
        if not self.does_user_with_username_exist(username):
            raise NotFoundError(f"No User with username: {username} found")

        try:
            self.table.update_item(
                Key={
                    "partition_key": "USER",
                    "username": username,
                },
                UpdateExpression="SET first_name = :fn, last_name = :ln, bio = :b",
                ExpressionAttributeValues={
                    ":fn": user_data.first_name,
                    ":ln": user_data.last_name,
                    ":b": user_data.bio,
                },
            )
        except ClientError as e:
            print(f"Error updating user in DynamoDB: {e}")
            raise BadRequestError(f"Error updating user in DynamoDB: {e}")

        return self.get_user_by_username_from_db(username)

    def get_user_by_username_from_db(self, username: str) -> User:
        response = self.table.query(
            ProjectionExpression="username, first_name, last_name, bio, scores",
            KeyConditionExpression=Key("partition_key").eq("USER")
            & Key("username").eq(username),
        )
        if not response.get("Items") or not response.get("Items")[0]:
            raise NotFoundError(f"No User with username: {username} found")

        try:
            return User(**response["Items"][0])
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to create user with provided parameters. {e}"
            )

    def get_users_by_username_prefix(self, username_prefix: str) -> [User]:
        response = self.table.query(
            ProjectionExpression="username, first_name, last_name, bio, scores",
            KeyConditionExpression=Key("partition_key").eq("USER")
            & Key("username").begins_with(username_prefix),
        )
        items = response["Items"]

        while "LastEvaluatedKey" in response:
            response = self.table.query(
                ProjectionExpression="username, first_name, last_name, bio, scores",
                ExclusiveStartKey=response["LastEvaluatedKey"],
                KeyConditionExpression=Key("partition_key").eq("USER")
                & Key("username").begins_with(username_prefix),
            )
            items.extend(response["Items"])

        try:
            users = [User(**item) for item in items]
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to create user with provided parameters. {e}"
            )

        return users

    def update_user_score_in_db(self, username: str, score: Score) -> User:
        try:
            self.table.update_item(
                Key={
                    "partition_key": "USER",
                    "username": username,
                },
                UpdateExpression="SET scores = list_append(scores, :i)",
                ExpressionAttributeValues={":i": [score.dict()]},
            )
        except ClientError as e:
            print(f"Error updating user scores in DynamoDB: {e}")
            raise BadRequestError(f"Error updating user scores in DynamoDB: {e}")

        return self.get_user_by_username_from_db(username)

    def does_user_with_username_exist(self, username: str) -> bool:
        response = self.table.query(
            KeyConditionExpression=Key("partition_key").eq("USER")
            & Key("username").eq(username),
            ProjectionExpression="username, first_name, last_name",
        )
        return "Items" in response and len(response["Items"]) > 0

    def __put_user_to_db(self, user: User) -> User:
        try:
            user = user.dict()
            user["partition_key"] = "USER"
            self.table.put_item(Item=user)
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

        return User(**user)
