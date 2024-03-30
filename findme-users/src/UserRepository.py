import uuid

import boto3
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
        if not self.__does_user_with_user_id_exist(user_id):
            raise NotFoundError(f"No User with user_id: {user_id} found")

        response = self.table.get_item(Key={'user_id': user_id})
        try:
            return User(**response["Item"])
        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to read Data from DB {e}")

    def get_users_by_username_prefix(self, username_prefix):
        # Handle the case where no username prefix is provided.
        if not username_prefix:
            return []

        # TODO works for now, scan is not really efficient though
        try:
            response = self.table.scan(
                FilterExpression='begins_with(username, :prefix)',
                ExpressionAttributeValues={
                    ':prefix': username_prefix
                }
            )

        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to read Data from DB {e}")

        return response.get('Items', [])

    def __does_user_with_user_id_exist(self, user_id):
        return 'Item' in self.table.get_item(Key={'user_id': user_id})

    def __put_user_to_db(self, user):
        try:
            self.table.put_item(Item=user.dict())
            return user
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")
