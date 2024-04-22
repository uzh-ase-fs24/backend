import uuid
import json
import boto3
import os

from typing import Union
from decimal import Decimal
from pydantic import ValidationError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
    InternalServerError
)
from src.helpers.CalculateScore import calculate_score_and_distance
from src.entities.LocationRiddle import LocationRiddle, LocationRiddleDTO, SolvedLocationRiddleDTO
from src.entities.Rating import Rating
from src.entities.Comment import Comment
from src.entities.Guess import Guess


class LocationRiddlesService:
    def __init__(self, location_riddle_repository, image_bucket_repository):
        self.image_bucket_repository = image_bucket_repository
        self.location_riddle_repository = location_riddle_repository

    def post_location_riddle(self, image_base64: str, location: list, user_id: str) -> dict:
        location_riddle_data = {
            "location_riddle_id": str(uuid.uuid4()),
            "user_id": user_id,
            "location": [Decimal(str(coord)) for coord in location]
        }

        try:
            location_riddle = LocationRiddle(**location_riddle_data)
        except ValidationError as e:
            print(f"unable to update location_riddle with provided parameters. {e}")
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        try:
            self.location_riddle_repository.write_location_riddle_to_db(location_riddle)
        except Exception as e:
            print(e)
            raise InternalServerError(e)

        image_path = f"location-riddles/{location_riddle.location_riddle_id}.png"
        return self.image_bucket_repository.post_image_to_s3(image_base64, image_path)

    def get_location_riddle(self, location_riddle_id: str, user_id: str) -> Union[LocationRiddleDTO, SolvedLocationRiddleDTO]:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        location_riddle_image = self.image_bucket_repository.get_image_from_s3(key)

        location_riddle_dto = location_riddle.to_dto(user_id=user_id)
        location_riddle_dto.image_base64 = location_riddle_image

        return location_riddle_dto

    def get_location_riddles_for_user(self, user_id: str, requester_id: str) -> list[Union[LocationRiddleDTO, SolvedLocationRiddleDTO]]:
        location_riddles = (
            self.location_riddle_repository.get_all_location_riddles_by_user_id(user_id)
        )
        if len(location_riddles) == 0:
            raise NotFoundError(
                f"No location riddles for user with user_id: {user_id} found"
            )

        location_riddles = [location_riddle.to_dto(requester_id) for location_riddle in location_riddles]
        for location_riddle in location_riddles:
            key = f"location-riddles/{location_riddle.location_riddle_id}.png"
            location_riddle.image_base64 = self.image_bucket_repository.get_image_from_s3(key)
        return location_riddles

    def get_location_riddles_feed(self, event, user_id: str) -> list[Union[LocationRiddleDTO, SolvedLocationRiddleDTO]]:
        following_users = self.__get_following_users_list(event, user_id)

        response = []
        for following_user in following_users:
            try:
                response.extend(self.get_location_riddles_for_user(user_id=following_user["user_id"], requester_id=user_id))
            except NotFoundError:
                continue
        return sorted(response, key=lambda riddle: riddle.created_at, reverse=True)

    def rate_location_riddle(self, location_riddle_id: str, user_id: str, rating: int) -> Union[LocationRiddleDTO, SolvedLocationRiddleDTO]:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id == user_id:
            raise BadRequestError("User cannot rate their own location riddle")
        for rating_entry in location_riddle.ratings:
            if rating_entry.user_id == user_id:
                raise BadRequestError("User has already rated this location riddle")

        try:
            rating = Rating(user_id=user_id, rating=rating)
        except ValidationError as e:
            print(f"unable to update location_riddle with provided parameters. {e}")
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        try:
            updated_location_riddle = self.location_riddle_repository.update_location_riddle_rating_in_db(
                location_riddle_id, rating
            )
        except Exception as e:
            print(e)
            raise BadRequestError(e)

        return updated_location_riddle.to_dto(user_id)

    def guess_location_riddle(self, event, location_riddle_id: str, user_id: str, guess: list) -> dict:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id == user_id:
            raise BadRequestError("User cannot guess their own location riddle")
        for guess_entry in location_riddle.guesses:
            if guess_entry.user_id == user_id:
                raise BadRequestError("User has already guessed this location riddle")

        try:
            guess = Guess(user_id=user_id, guess=[Decimal(str(coord)) for coord in guess])
        except ValidationError as e:
            print(f"unable to update location_riddle with provided parameters. {e}")
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        try:
            updated_location_riddle = self.location_riddle_repository.update_location_riddle_guesses_in_db(
                location_riddle_id, guess
            )
        except Exception as e:
            print(e)
            raise BadRequestError(e)

        score, distance = calculate_score_and_distance(
            map(float, tuple(updated_location_riddle.location)),
            map(float, tuple(guess.guess))
        )

        try:
            self.__write_score_to_user_in_user_db(event, location_riddle_id, int(score))
        except Exception as e:
            print(f"There was an error writing the score to the user db: {e}")

        return {
            "location_riddle": updated_location_riddle.to_dto(user_id).dict(),
            "guess_result": {"distance": distance, "received_score": score}
        }

    def comment_location_riddle(self, location_riddle_id: str, user_id: str, comment: str) -> Union[LocationRiddleDTO, SolvedLocationRiddleDTO]:
        try:
            comment = Comment(user_id=user_id, comment=comment)
        except ValidationError as e:
            print(f"unable to update location_riddle with provided parameters. {e}")
            raise BadRequestError(f"unable to update location_riddle with provided parameters. {e}")

        try:
            updated_location_riddle = self.location_riddle_repository.update_location_riddle_comments_in_db(
                location_riddle_id, comment
            )
        except Exception as e:
            print(e)
            raise BadRequestError(e)

        return updated_location_riddle.to_dto(user_id)

    def delete_location_riddle(self, location_riddle_id: str, user_id: str) -> dict:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id != user_id:
            raise BadRequestError("User does not have permission to delete this location riddle")

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        self.image_bucket_repository.delete_image_from_s3(key)
        self.location_riddle_repository.delete_location_riddle_from_db(location_riddle_id)
        return {"message": "Location riddle deleted successfully"}

    def __get_following_users_list(self, event, user_id: str):
        event_dict = dict(event)
        event_dict["path"] = f"/users/{user_id}/follow"
        client = boto3.client("lambda", region_name="eu-central-2")
        response = client.invoke(FunctionName=os.environ["USER_FUNCTION_NAME"], Payload=json.dumps(event_dict))

        streaming_body = response['Payload']
        payload_bytes = streaming_body.read()
        payload_str = payload_bytes.decode('utf-8')
        payload_dict = json.loads(payload_str)
        user_connections = json.loads(payload_dict['body'])

        return user_connections['following']

    def __write_score_to_user_in_user_db(self, event, location_riddle_id: str, score: str):
        event_dict = dict(event)
        event_dict["path"] = f"/users/score"
        event_dict["body"] = json.dumps({"score": score, "location_riddle_id": location_riddle_id})
        client = boto3.client("lambda", region_name="eu-central-2")
        _ = client.invoke(FunctionName=os.environ["USER_FUNCTION_NAME"], Payload=json.dumps(event_dict))
