import json
import math
import os
import uuid
from decimal import Decimal
from typing import Union
from urllib.parse import urljoin

import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
    InternalServerError,
)
from aws_lambda_powertools.logging import Logger
from pydantic import ValidationError

from .entities.Comment import Comment
from .entities.Coordinate import Coordinate
from .entities.Guess import Guess
from .entities.LocationRiddle import (
    LocationRiddle,
    LocationRiddleDTO,
    SolvedLocationRiddleDTO,
)
from .entities.Rating import Rating

logger = Logger()


class LocationRiddlesService:
    def __init__(self, location_riddle_repository, image_bucket_repository):
        self.image_bucket_repository = image_bucket_repository
        self.location_riddle_repository = location_riddle_repository

    def post_location_riddle(
        self, image_base64: str, location: list, username: str
    ) -> dict:
        try:
            location_riddle = LocationRiddle(
                location_riddle_id=str(uuid.uuid4()),
                username=username,
                location=Coordinate(
                    coordinate=[Decimal(str(coord)) for coord in location]
                ),
            )
        except ValidationError as e:
            logger.info(
                f"unable to update location_riddle with provided parameters. {e}"
            )
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        image_path = f"location-riddles/{location_riddle.location_riddle_id}.png"
        response = self.image_bucket_repository.post_image_to_s3(
            image_base64, image_path
        )

        try:
            self.location_riddle_repository.write_location_riddle_to_db(location_riddle)
        except Exception as e:
            logger.error(e)
            raise InternalServerError(f"{e}")
        return response

    def get_location_riddle(
        self, location_riddle_id: str, username: str
    ) -> Union[LocationRiddleDTO, SolvedLocationRiddleDTO]:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        location_riddle_dto = location_riddle.to_dto(username=username)
        self.__append_image_to_location_riddle(location_riddle_dto)
        return location_riddle_dto

    def get_location_riddles_for_user(
        self, username: str, requester_username: str
    ) -> list[Union[LocationRiddleDTO, SolvedLocationRiddleDTO]]:
        location_riddles = (
            self.location_riddle_repository.get_all_location_riddles_by_username(
                username
            )
        )
        if len(location_riddles) == 0:
            raise NotFoundError(
                f"No location riddles for user with username: {username} found"
            )

        location_riddle_dtos = [
            location_riddle.to_dto(requester_username)
            for location_riddle in location_riddles
        ]
        for location_riddle_dto in location_riddle_dtos:
            self.__append_image_to_location_riddle(location_riddle_dto)
        return location_riddle_dtos

    def get_solved_location_riddles_for_user(
        self, event, username: str, requester_username: str
    ) -> list[Union[LocationRiddleDTO, SolvedLocationRiddleDTO]]:
        location_riddle_ids = [location_riddle["location_riddle_id"] for location_riddle in self.__get_user_scores(event, username)]

        if len(location_riddle_ids) == 0:
            raise NotFoundError(
                f"No location riddles for user with username: {username} found"
            )

        location_riddles = [
            self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(location_riddle_id)
            for location_riddle_id in location_riddle_ids
        ]

        location_riddle_dtos = [
            location_riddle.to_dto(requester_username)
            for location_riddle in location_riddles
        ]
        for location_riddle_dto in location_riddle_dtos:
            self.__append_image_to_location_riddle(location_riddle_dto)
        return location_riddle_dtos

    def get_location_riddles_feed(
        self, event, username: str
    ) -> list[Union[LocationRiddleDTO, SolvedLocationRiddleDTO]]:
        following_users = self.__get_following_users_list(event, username)

        response = []
        for following_user in following_users:
            try:
                response.extend(
                    self.get_location_riddles_for_user(
                        username=following_user["username"], requester_username=username
                    )
                )
            except NotFoundError:
                continue
        return sorted(response, key=lambda riddle: riddle.created_at, reverse=True)

    def rate_location_riddle(
        self, location_riddle_id: str, username: str, rating: int
    ) -> Union[LocationRiddleDTO, SolvedLocationRiddleDTO]:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.username == username:
            raise BadRequestError("User cannot rate their own location riddle")
        for rating_entry in location_riddle.ratings:
            if rating_entry.username == username:
                raise BadRequestError("User has already rated this location riddle")

        try:
            rating = Rating(username=username, rating=rating)
        except ValidationError as e:
            logger.info(
                f"unable to update location_riddle with provided parameters. {e}"
            )
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        try:
            updated_location_riddle = (
                self.location_riddle_repository.update_location_riddle_rating_in_db(
                    location_riddle_id, rating
                )
            )
        except Exception as e:
            logger.error(e)
            raise BadRequestError(f"{e}")

        location_riddle_dto = updated_location_riddle.to_dto(username)
        self.__append_image_to_location_riddle(location_riddle_dto)
        return location_riddle_dto

    def guess_location_riddle(
        self, event, location_riddle_id: str, username: str, guess: list
    ) -> dict:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.username == username:
            raise BadRequestError("User cannot guess their own location riddle")
        for guess_entry in location_riddle.guesses:
            if guess_entry.username == username:
                raise BadRequestError("User has already guessed this location riddle")

        try:
            guess = Guess(
                username=username,
                guess=Coordinate(coordinate=[Decimal(str(coord)) for coord in guess]),
            )
        except ValidationError as e:
            logger.info(
                f"unable to update location_riddle with provided parameters. {e}"
            )
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        try:
            updated_location_riddle = (
                self.location_riddle_repository.update_location_riddle_guesses_in_db(
                    location_riddle_id, guess
                )
            )
        except Exception as e:
            logger.error(e)
            raise BadRequestError(f"{e}")

        score, distance = LocationRiddlesService.calculate_score_and_distance(
            [float(coord) for coord in updated_location_riddle.location.coordinate],
            [float(coord) for coord in guess.guess.coordinate],
        )

        try:
            self.__write_score_to_user_in_user_db(event, location_riddle_id, int(score))
        except Exception as e:
            logger.error(f"There was an error writing the score to the user db: {e}")

        location_riddle_dto = updated_location_riddle.to_dto(username)
        self.__append_image_to_location_riddle(location_riddle_dto)
        return {
            "location_riddle": location_riddle_dto.dict(),
            "guess_result": {"distance": distance, "received_score": score},
        }

    def comment_location_riddle(
        self, location_riddle_id: str, username: str, comment: str
    ) -> Union[LocationRiddleDTO, SolvedLocationRiddleDTO]:
        try:
            comment = Comment(username=username, comment=comment)
        except ValidationError as e:
            logger.info(
                f"unable to update location_riddle with provided parameters. {e}"
            )
            raise BadRequestError(
                f"unable to update location_riddle with provided parameters. {e}"
            )

        try:
            updated_location_riddle = (
                self.location_riddle_repository.update_location_riddle_comments_in_db(
                    location_riddle_id, comment
                )
            )
        except Exception as e:
            logger.error(e)
            raise BadRequestError(f"{e}")

        location_riddle_dto = updated_location_riddle.to_dto(username)
        self.__append_image_to_location_riddle(location_riddle_dto)
        return location_riddle_dto

    def delete_location_riddle(self, location_riddle_id: str, username: str) -> dict:
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.username != username:
            raise BadRequestError(
                "User does not have permission to delete this location riddle"
            )

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        self.image_bucket_repository.delete_image_from_s3(key)
        self.location_riddle_repository.delete_location_riddle_from_db(
            location_riddle_id
        )
        return {"message": "Location riddle deleted successfully"}

    def __get_following_users_list(self, event, username: str):
        event_dict = dict(event)
        base_url = "/users/"
        event_dict["path"] = urljoin(base_url, f"{username}/follow")
        client = boto3.client("lambda", region_name="eu-central-2")
        response = client.invoke(
            FunctionName=os.environ["USER_FUNCTION_NAME"],
            Payload=json.dumps(event_dict),
        )

        streaming_body = response["Payload"]
        payload_bytes = streaming_body.read()
        payload_str = payload_bytes.decode("utf-8")
        payload_dict = json.loads(payload_str)
        user_connections = json.loads(payload_dict["body"])

        return user_connections["following"]

    def __get_user_scores(self, event, username: str):
        event_dict = dict(event)
        base_url = "/users/"
        event_dict["path"] = urljoin(base_url, f"{username}/scores")
        client = boto3.client("lambda", region_name="eu-central-2")
        response = client.invoke(
            FunctionName=os.environ["USER_FUNCTION_NAME"],
            Payload=json.dumps(event_dict),
        )

        streaming_body = response["Payload"]
        payload_bytes = streaming_body.read()
        payload_str = payload_bytes.decode("utf-8")
        payload_dict = json.loads(payload_str)
        user_scores = json.loads(payload_dict["body"])

        return user_scores

    def __write_score_to_user_in_user_db(
        self, event, location_riddle_id: str, score: int
    ):
        event_dict = dict(event)
        event_dict["path"] = "/users/score"
        event_dict["body"] = json.dumps(
            {"score": score, "location_riddle_id": location_riddle_id}
        )
        client = boto3.client("lambda", region_name="eu-central-2")
        _ = client.invoke(
            FunctionName=os.environ["USER_FUNCTION_NAME"],
            Payload=json.dumps(event_dict),
        )

    def __append_image_to_location_riddle(self, location_riddle: LocationRiddle):
        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        location_riddle.image_base64 = self.image_bucket_repository.get_image_from_s3(
            key
        )

    @staticmethod
    def calculate_score_and_distance(
        actual_coord, guessed_coord, max_score=10000, distance_penalty=100
    ):
        distance = (
            math.sqrt(
                (actual_coord[0] - guessed_coord[0]) ** 2
                + (actual_coord[1] - guessed_coord[1]) ** 2
            )
            / 1000
        )

        # Calculate score with simple linear penalty
        score = max(0, max_score - distance * distance_penalty)
        return score, distance
