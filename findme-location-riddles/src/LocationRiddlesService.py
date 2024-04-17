import uuid
import json
import boto3
import os

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class LocationRiddlesService:
    def __init__(self, location_riddle_repository, image_bucket_repository):
        self.image_bucket_repository = image_bucket_repository
        self.location_riddle_repository = location_riddle_repository

    def post_location_riddle(self, image_base64, location, user_id):
        location_riddle_id = str(uuid.uuid4())
        image_path = f"location-riddles/{location_riddle_id}.png"

        try:
            self.location_riddle_repository.write_location_riddle_to_db(
                user_id, location_riddle_id, location
            )
        except Exception as e:
            raise BadRequestError(e)

        return self.image_bucket_repository.post_image_to_s3(image_base64, image_path)

    def get_location_riddle(self, location_riddle_id):
        # TODO: check if requesting user is following the user_id
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        location_riddle_image = self.image_bucket_repository.get_image_from_s3(key)

        return location_riddle.dict(exclude={"ratings"}) | {"location_riddle_image": location_riddle_image}

    def get_location_riddles_for_user(self, user_id):
        # TODO: check if requesting user is following the user_id
        location_riddles = (
            self.location_riddle_repository.get_all_location_riddles_by_user_id(user_id)
        )
        if len(location_riddles) == 0:
            raise NotFoundError(
                f"No location riddles for user with user_id: {user_id} found"
            )

        response = []
        for location_riddle in location_riddles:
            key = f"location-riddles/{location_riddle.location_riddle_id}.png"
            location_riddle_image = self.image_bucket_repository.get_image_from_s3(key)
            response.append(
                location_riddle.dict(exclude={"ratings"})
                | {"location_riddle_image": location_riddle_image}
            )
        return response

    def get_location_riddles_feed(self, event, user):
        following_users = self.__get_following_users_list(event, user)

        response = []
        for user in following_users:
            try:
                response.extend(self.get_location_riddles_for_user(user["user_id"]))
            except NotFoundError:
                continue
        return response

    def rate_location_riddle(self, location_riddle_id, user_id, rating):
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id == user_id:
            raise BadRequestError("User cannot rate their own location riddle")
        for rating_entry in location_riddle.ratings:
            if rating_entry.user_id == user_id:
                raise BadRequestError("User has already rated this location riddle")
        # TODO: check if requesting user is following the user_id

        try:
            response = self.location_riddle_repository.update_location_riddle_rating_in_db(
                location_riddle_id, user_id, rating
            )
        except Exception as e:
            raise BadRequestError(e)

        return response.dict(exclude={"ratings"})

    def guess_location_riddle(self, location_riddle_id, user_id, guess):
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id == user_id:
            raise BadRequestError("User cannot guess their own location riddle")
        for guess_entry in location_riddle.guesses:
            if guess_entry.user_id == user_id:
                raise BadRequestError("User has already guessed this location riddle")
        # TODO: check if requesting user is following the user_id

        try:
            response = self.location_riddle_repository.update_location_riddle_guesses_in_db(
                location_riddle_id, user_id, guess
            )
        except Exception as e:
            raise BadRequestError(e)

        return response.dict(exclude={"ratings"})

    def comment_location_riddle(self, location_riddle_id, user_id, comment):
        try:
            response = self.location_riddle_repository.update_location_riddle_comments_in_db(
                location_riddle_id, user_id, comment
            )
        except Exception as e:
            raise BadRequestError(e)

        return response.dict(exclude={"ratings"})

    def delete_location_riddle(self, location_riddle_id, user_id):
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id != user_id:
            raise BadRequestError("User does not have permission to delete this location riddle")

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        self.image_bucket_repository.delete_image_from_s3(key)
        self.location_riddle_repository.delete_location_riddle_from_db(location_riddle_id)
        return {"message": "Location riddle deleted successfully"}

    def __get_following_users_list(self, event, user_id):
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
