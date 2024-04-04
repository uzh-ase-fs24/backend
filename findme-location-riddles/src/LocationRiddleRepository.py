import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pydantic import ValidationError
from src.LocationRiddle import LocationRiddle


class LocationRiddleRepository:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-central-2")
        self.table = self.dynamodb.Table("locationRiddleTable")

    def write_location_riddle_to_db(self, user_id, location_riddle_id):
        location_riddle_data = {
            "location_riddle_id": location_riddle_id,
            "user_id": user_id,
        }

        try:
            location_riddle = LocationRiddle(**location_riddle_data)
        except ValidationError as e:
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        try:
            self.table.put_item(Item=location_riddle.dict())
        except ClientError as e:
            print(f"Error writing location_riddle to DynamoDB: {e}")
            raise BadRequestError(f"Error writing location_riddle to DynamoDB: {e}")

    def get_all_location_riddles_by_user_id(self, user_id):
        response = self.table.query(
            IndexName="UserIndex", KeyConditionExpression=Key("user_id").eq(user_id)
        )
        items = response["Items"]

        while "LastEvaluatedKey" in response:
            response = self.table.query(
                IndexName="UserIndex",
                ExclusiveStartKey=response["LastEvaluatedKey"],
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            items.extend(response["Items"])

        try:
            location_riddles = [LocationRiddle(**item) for item in items]
        except ValidationError as e:
            raise BadRequestError(f"Unable to read Data from DB {e}")

        return location_riddles

    def get_location_riddle_by_location_riddle_id_from_db(self, location_riddle_id):
        response = self.table.get_item(Key={"location_riddle_id": location_riddle_id})

        if "Item" not in response:
            raise NotFoundError(
                f"No location riddle with location_riddle_id: {location_riddle_id} found"
            )
        try:
            location_riddle = LocationRiddle(**response["Item"])
        except ValidationError as e:
            raise BadRequestError(f"Unable to read Data from DB {e}")

        return location_riddle
