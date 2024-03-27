import boto3
from src.UserImages import UserImages
from botocore.exceptions import ClientError
from pydantic import ValidationError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class ImageDbRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('usersImageTable')

    def write_image_to_db(self, user_id, image_id):
        if not self.__does_user_with_user_id_exist(user_id):
            user_images_data = {"user_id": user_id, "image_ids": [image_id]}
        else:
            response = self.table.get_item(Key={'user_id': user_id})
            user_images_data = response["Item"].copy()
            user_images_data["image_ids"].append(image_id)

        try:
            user_images = UserImages(**user_images_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to update user_images with provided parameters. {e}")

        try:
            self.table.put_item(Item=user_images.dict())
        except ClientError as e:
            print(f"Error writing user_images to DynamoDB: {e}")
            raise BadRequestError(f"Error writing user_images to DynamoDB: {e}")

    def get_all_image_ids_for_user(self, user_id):
        if not self.__does_user_with_user_id_exist(user_id):
            raise NotFoundError(f"No User with user_id: {user_id} found")
        response = self.table.get_item(Key={'user_id': user_id})
        return response["Item"]["image_ids"].copy()

    def __does_user_with_user_id_exist(self, user_id):
        return 'Item' in self.table.get_item(Key={'user_id': user_id})