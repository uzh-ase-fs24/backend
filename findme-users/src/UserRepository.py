import boto3
from botocore.exceptions import ClientError
from src.User import User
from pydantic import ValidationError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class UserRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('usersTable')
    
    def post_user_to_db(self, user):
        try:
            # simply return the user if there is already one for a given token
            if self.__does_user_with_userId_exist(user.userId):
                raise BadRequestError(f"User with id {user.userId} already has an account")

            self.table.put_item(Item=user.dict())
            return user
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

    def update_user_in_db(self, user):
        try:
            if self.__does_user_with_userId_exist(user.userId):
                self.table.put_item(Item=user.dict())
                return user
            else:
                raise NotFoundError(f"No User with userId: {user.userId} found")


        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")

    def get_user_by_userId_from_db(self, userId):
        response = self.table.get_item(Key={'userId': userId})
        if "Item" not in response:
            raise NotFoundError(f"No User with userId: {userId} found")

        try:
            return User(**response["Item"])
        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to read Data from DB {e}")

    def __does_user_with_userId_exist(self, userId):
        if 'Item' in self.table.get_item(Key={'userId': userId}):
            return True
        else:
            return False