import boto3
from botocore.exceptions import ClientError
from src.UserDto import UserDto

class UserRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('usersTable')
    
    def post_user_to_db(self, user):
        try:
            self.table.put_item(Item=user.dict())
            return user, 200  
        
        except ClientError as e:
            print("Error saving user to DynamoDB:", e)
            return e, 500 
        
    def get_user_by_userId_from_db(self, userId):
        try:
            response = self.table.get_item(Key={'userId': userId})
            return UserDto(**response["Item"]), 200 
        
        except ClientError as e:
            print("Error getting the User by userId:", e)
            return e, 404