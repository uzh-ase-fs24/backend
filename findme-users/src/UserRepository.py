import boto3
from boto3.dynamodb.conditions import Key
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from botocore.exceptions import ClientError
from pydantic import ValidationError
from src.entities.User import User


class UserRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('usersTable')

    def post_user_to_db(self, user):
        if self.__does_user_with_user_id_exist(user.user_id):
            raise BadRequestError(f"User with id {user.user_id} already has an account")

        return self.__put_user_to_db(user)

    def update_user_in_db(self, user):
        if not self.__does_user_with_user_id_exist(user.user_id):
            raise NotFoundError(f"No User with user_id: {user.user_id} found")

        return self.__put_user_to_db(user)

    def get_user_by_user_id_from_db(self, user_id):
        response = self.table.query(
            IndexName="UserIdIndex",
            ProjectionExpression="user_id, username, first_name, last_name",
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        if not response.get('Items'):
            raise NotFoundError(f"No User with user_id: {user_id} found")
        try:
            return User(**response["Item"])
        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to read Data from DB {e}")

    def get_users_by_username_prefix(self, username_prefix):
        # Handle the case where no username prefix is provided.
        if not username_prefix:
            return []

        try:
            response = self.table.query(
                ProjectionExpression="user_id, username, first_name, last_name",
                KeyConditionExpression=Key('partition_key').eq("USER") & Key('username').begins_with(username_prefix)
            )

        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to read Data from DB {e}")

        return response.get('Items', [])

    def __does_user_with_user_id_exist(self, user_id):
        return 'Item' in self.table.query(
            IndexName="UserIdIndex",
            KeyConditionExpression=Key('partition_key').eq("USER") & Key('user_id').eq(user_id),
            ProjectionExpression="user_id, username, first_name, last_name"
        )

    def __put_user_to_db(self, user):
        try:
            user = user.dict()
            user['partition_key'] = "USER"
            self.table.put_item(Item=user)
            return user
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")
