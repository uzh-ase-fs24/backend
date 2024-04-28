import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pydantic import ValidationError

from .base.AbstractLocationRiddlesRepository import AbstractLocationRiddlesRepository
from .entities.Comment import Comment
from .entities.Guess import Guess
from .entities.LocationRiddle import LocationRiddle
from .entities.Rating import Rating

logger = Logger()


class LocationRiddlesRepository(AbstractLocationRiddlesRepository):
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-central-2")
        self.table = self.dynamodb.Table("locationRiddleTable")

    def write_location_riddle_to_db(self, location_riddle: LocationRiddle):
        try:
            self.table.put_item(Item=location_riddle.dict())
        except Exception as e:
            logger.error(f"Error writing location_riddle to DynamoDB: {e}")
            raise BadRequestError(f"Error writing location_riddle to DynamoDB: {e}")

    def get_all_location_riddles_by_username(self, username: str):
        response = self.table.query(
            IndexName="UserIndex", KeyConditionExpression=Key("username").eq(username)
        )
        items = response["Items"]

        while "LastEvaluatedKey" in response:
            response = self.table.query(
                IndexName="UserIndex",
                ExclusiveStartKey=response["LastEvaluatedKey"],
                KeyConditionExpression=Key("username").eq(username),
            )
            items.extend(response["Items"])

        try:
            location_riddles = [LocationRiddle(**item) for item in items]
        except ValidationError as e:
            logger.info(f"Unable to read Data from DB {e}")
            raise BadRequestError(f"Unable to read Data from DB {e}")

        return location_riddles

    def get_location_riddle_by_location_riddle_id_from_db(
        self, location_riddle_id: str
    ):
        response = self.table.get_item(Key={"location_riddle_id": location_riddle_id})

        if "Item" not in response:
            raise NotFoundError(
                f"No location riddle with location_riddle_id: {location_riddle_id} found"
            )
        try:
            location_riddle = LocationRiddle(**response["Item"])
        except ValidationError as e:
            logger.info(f"Unable to read Data from DB {e}")
            raise BadRequestError(f"Unable to read Data from DB {e}")

        return location_riddle

    def update_location_riddle_rating_in_db(
        self, location_riddle_id: str, rating: Rating
    ):
        return self.__append_attribute(location_riddle_id, "ratings", rating)

    def update_location_riddle_comments_in_db(
        self, location_riddle_id: str, comment: Comment
    ):
        return self.__append_attribute(location_riddle_id, "comments", comment)

    def update_location_riddle_guesses_in_db(
        self, location_riddle_id: str, guess: Guess
    ):
        return self.__append_attribute(location_riddle_id, "guesses", guess)

    def delete_location_riddle_from_db(self, location_riddle_id: str):
        try:
            self.table.delete_item(Key={"location_riddle_id": location_riddle_id})
        except ClientError as e:
            logger.error(f"Error deleting location_riddle from DynamoDB: {e}")
            raise BadRequestError(f"Error deleting location_riddle from DynamoDB: {e}")

    def __append_attribute(self, location_riddle_id, attribute, value):
        try:
            self.table.update_item(
                Key={"location_riddle_id": location_riddle_id},
                UpdateExpression=f"SET {attribute} = list_append({attribute}, :i)",
                ExpressionAttributeValues={":i": [value.dict()]},
            )
        except ClientError as e:
            logger.error(f"Error updating location_riddle {attribute} in DynamoDB: {e}")
            raise BadRequestError(
                f"Error updating location_riddle {attribute} in DynamoDB: {e}"
            )

        return self.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )
