import uuid
import requests

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from src.ImageBucketRepository import ImageBucketRepository
from src.LocationRiddleRepository import LocationRiddleRepository


class LocationRiddlesService:
    def __init__(self):
        self.image_bucket_repository = ImageBucketRepository()
        self.location_riddle_repository = LocationRiddleRepository()

    def post_location_riddle(self, image_base64, user_id):
        location_riddle_id = str(uuid.uuid4())
        image_path = f"location-riddles/{location_riddle_id}.png"

        try:
            self.location_riddle_repository.write_location_riddle_to_db(
                user_id, location_riddle_id
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

        return location_riddle.dict() | {"location_riddle_image": location_riddle_image}

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
                location_riddle.dict()
                | {"location_riddle_image": location_riddle_image}
            )
        return response

    def get_location_riddles_feed(self, token, user_id):
        # TODO: Implement API call to findme-user service to get the list of users that the current user follows
        url = f"http://localhost:4566/restapis/findme/local/_user_request_/users/{user_id}"
        headers = {'Authorization': token}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"GET /users/{user_id} failed with status {response.status_code}.")
        print(response.json())

        following_users = ["660e5fc5de3e93a3b75f51a8", "0FhpaZeIjhSG1lwNR3RWPI20VgLgU5rk@clients"]
        response = []
        for user_id in following_users:
            try:
                response.extend(self.get_location_riddles_for_user(user_id))
            except NotFoundError:
                continue
        return response

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