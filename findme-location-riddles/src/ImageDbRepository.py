import boto3
from src.LocationRiddle import LocationRiddle
from botocore.exceptions import ClientError
from pydantic import ValidationError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class ImageDbRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('locationRiddleTable')

    def write_location_riddle_to_db(self, user_id, image_id):
        location_riddle_data = {"location_riddle_id": image_id, "user_id": user_id}
        # response = self.table.get_item(Key={'user_id': user_id})
        # location_riddle_data = response["Item"].copy()
        # location_riddle_data["image_ids"].append(image_id)

        try:
            location_riddle = LocationRiddle(**location_riddle_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        try:
            self.table.put_item(Item=location_riddle.dict())
        except ClientError as e:
            print(f"Error writing location_riddle to DynamoDB: {e}")
            raise BadRequestError(f"Error writing location_riddle to DynamoDB: {e}")

    def get_all_image_ids_for_user(self, user_id):
        if not self.__does_user_with_user_id_exist(user_id):
            raise NotFoundError(f"No User with user_id: {user_id} found")
        response = self.table.get_item(Key={'user_id': user_id})
        return response["Item"]["image_ids"].copy()

    def __does_user_with_user_id_exist(self, user_id):
        return 'Item' in self.table.get_item(Key={'user_id': user_id})