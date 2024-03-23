import boto3
from botocore.exceptions import ClientError
from src.UserDto import UserDto
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
            self.table.put_item(Item=user.dict())
            return user
        except ClientError as e:
            print(f"Error saving user to DynamoDB: {e}")
            raise BadRequestError(f"Error saving user to DynamoDB: {e}")
        
    def get_user_by_userId_from_db(self, userId):
        response = self.table.get_item(Key={'userId': userId})
        if "Item" not in response:
            raise NotFoundError(f"No User with userId: {userId} found")

        try:
            return UserDto(**response["Item"])
        except ValidationError as e:
            print(e)
            raise BadRequestError(f"Unable to read Data from DB {e}")