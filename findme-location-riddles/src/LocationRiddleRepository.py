import boto3
from src.LocationRiddle import LocationRiddle
from botocore.exceptions import ClientError
from pydantic import ValidationError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class LocationRiddleRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
        self.table = self.dynamodb.Table('locationRiddleTable')

    def write_location_riddle_to_db(self, user_id, image_id):
        location_riddle_data = {"location_riddle_id": image_id, "user_id": user_id}

        try:
            location_riddle = LocationRiddle(**location_riddle_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        try:
            self.table.put_item(Item=location_riddle.dict())
        except ClientError as e:
            print(f"Error writing location_riddle to DynamoDB: {e}")
            raise BadRequestError(f"Error writing location_riddle to DynamoDB: {e}")

    def get_all_location_riddles(self):
        # ToDo: do the scanning by user_id here instead of LocationRiddlesService.get_location_riddles_for_user()
        response = self.table.scan()
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return data
