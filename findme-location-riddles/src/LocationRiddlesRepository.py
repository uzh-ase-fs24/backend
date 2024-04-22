from decimal import Decimal

import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pydantic import ValidationError
from src.entities.LocationRiddle import LocationRiddle
from src.entities.Rating import Rating
from src.entities.Comment import Comment
from src.entities.Guess import Guess
from src.base.AbstractLocationRiddlesRepository import AbstractLocationRiddlesRepository


class LocationRiddlesRepository(AbstractLocationRiddlesRepository):
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-central-2")
        self.table = self.dynamodb.Table("locationRiddleTable")

    def write_location_riddle_to_db(self, user_id, location_riddle_id, location):
        location_riddle_data = {
            "location_riddle_id": location_riddle_id,
            "user_id": user_id,
            "location": [Decimal(str(coord)) for coord in location]
        }

        try:
            location_riddle = LocationRiddle(**location_riddle_data)
        except ValidationError as e:
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        try:
            self.table.put_item(Item=location_riddle.dict())
        except Exception as e:
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

    def update_location_riddle_rating_in_db(self, location_riddle_id, user_id, rating):
        try:
            rating = Rating(user_id=user_id, rating=rating)
        except ValidationError as e:
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        return self.__append_attribute(location_riddle_id, "ratings", rating)

    def update_location_riddle_comments_in_db(self, location_riddle_id, user_id, comment):
        try:
            comment = Comment(user_id=user_id, comment=comment)
        except ValidationError as e:
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        return self.__append_attribute(location_riddle_id, "comments", comment)

    def update_location_riddle_guesses_in_db(self, location_riddle_id, user_id, guess):
        try:
            guess = Guess(user_id=user_id, guess=[Decimal(str(coord)) for coord in guess])
        except ValidationError as e:
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        return self.__append_attribute(location_riddle_id, "guesses", guess)

    def delete_location_riddle_from_db(self, location_riddle_id):
        try:
            self.table.delete_item(Key={"location_riddle_id": location_riddle_id})
        except ClientError as e:
            print(f"Error deleting location_riddle from DynamoDB: {e}")
            raise BadRequestError(f"Error deleting location_riddle from DynamoDB: {e}")

    def __append_attribute(self, location_riddle_id, attribute, value):
        try:
            self.table.update_item(
                Key={"location_riddle_id": location_riddle_id},
                UpdateExpression=f"SET {attribute} = list_append({attribute}, :i)",
                ExpressionAttributeValues={":i": [value.dict()]},
            )
        except ClientError as e:
            print(f"Error updating location_riddle {attribute} in DynamoDB: {e}")
            raise BadRequestError(f"Error updating location_riddle {attribute} in DynamoDB: {e}")

        return self.get_location_riddle_by_location_riddle_id_from_db(location_riddle_id)
