import boto3
from boto3.dynamodb.conditions import Key
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from botocore.exceptions import ClientError
from pydantic import ValidationError
from src.entities.User import User, UserPutDTO
from src.base.AbstractUserRepository import AbstractUserRepository
from src.entities.Score import Score


class UserRepository(AbstractUserRepository):
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('usersTable')

    def post_user_to_db(self, user: User) -> User:
        if self.does_user_with_user_id_exist(user.user_id):
            raise BadRequestError(f"User with id {user.user_id} already has an account!")
        if self.__does_user_with_username_exist(user.username):
            raise BadRequestError(f"Username '{user.username}' is already taken!")

        return self.__put_user_to_db(user)

    def update_user_in_db(self, user_id: str, user_data: UserPutDTO) -> User:
        if not self.does_user_with_user_id_exist(user_id):
            raise NotFoundError(f"No User with user_id: {user_id} found")

        try:
            self.table.update_item(
                Key={
                    'partition_key': 'USER',
                    'username': self.get_user_by_user_id_from_db(user_id).username
                },
                UpdateExpression="SET first_name = :fn, last_name = :ln",
                ExpressionAttributeValues={
                    ':fn': user_data.first_name,
                    ':ln': user_data.last_name
                },
            )
        except ClientError as e:
            print(f"Error updating user in DynamoDB: {e}")
            raise BadRequestError(f"Error updating user in DynamoDB: {e}")

        return self.get_user_by_user_id_from_db(user_id)

    def get_user_by_user_id_from_db(self, user_id: str) -> User:
        response = self.table.query(
            IndexName="UserIdIndex",
            ProjectionExpression="user_id, username, first_name, last_name, scores",
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        if not response.get('Items') or not response.get('Items')[0]:
            raise NotFoundError(f"No User with user_id: {user_id} found")

        try:
            return User(**response["Items"][0])
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(f"unable to create user with provided parameters. {e}")

    def get_users_by_username_prefix(self, username_prefix: str) -> [User]:
        response = self.table.query(
            ProjectionExpression="user_id, username, first_name, last_name, scores",
            KeyConditionExpression=Key('partition_key').eq("USER") & Key('username').begins_with(username_prefix)
        )
        items = response["Items"]

        while "LastEvaluatedKey" in response:
            response = self.table.query(
                ProjectionExpression="user_id, username, first_name, last_name",
                ExclusiveStartKey=response["LastEvaluatedKey"],
                KeyConditionExpression=Key('partition_key').eq("USER") & Key('username').begins_with(username_prefix)
            )
            items.extend(response["Items"])

        try:
            users = [User(**item) for item in items]
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(f"unable to create user with provided parameters. {e}")

        return users

    def update_user_score_in_db(self, user_id: str, score: Score) -> User:
        try:
            self.table.update_item(
                Key={
                    'partition_key': 'USER',
                    'username': self.get_user_by_user_id_from_db(user_id).username
                },
                UpdateExpression="SET scores = list_append(scores, :i)",
                ExpressionAttributeValues={":i": [score.dict()]},
            )
        except ClientError as e:
            print(f"Error updating user scores in DynamoDB: {e}")
            raise BadRequestError(f"Error updating user scores in DynamoDB: {e}")

        return self.get_user_by_user_id_from_db(user_id)

    def does_user_with_user_id_exist(self, user_id: str) -> bool:
        response = self.table.query(
            IndexName="UserIdIndex",
            KeyConditionExpression=Key('user_id').eq(user_id),
            ProjectionExpression="user_id, username, first_name, last_name"
        )
        return 'Items' in response and len(response['Items']) > 0

    def __does_user_with_username_exist(self, username: str) -> bool:
        response = self.table.query(
            KeyConditionExpression=Key('partition_key').eq('USER') & Key('username').eq(username),
            ProjectionExpression="user_id, username, first_name, last_name"
        )
        return 'Items' in response and len(response['Items']) > 0

    def __put_user_to_db(self, user: User) -> User:
        try:
            user = user.dict()
            user['partition_key'] = "USER"
            self.table.put_item(Item=user)
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

        return User(**user)
