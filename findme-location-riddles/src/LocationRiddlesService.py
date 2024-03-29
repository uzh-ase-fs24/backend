from src.ImageBucketRepository import ImageBucketRepository
from src.LocationRiddleRepository import LocationRiddleRepository
import uuid
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError
)

class LocationRiddlesService:
    def __init__(self):
        self.image_bucket_repository = ImageBucketRepository()
        self.location_riddle_repository = LocationRiddleRepository()

    def post_location_riddle(self, image_base64, user_id):
        image_id = str(uuid.uuid4())
        image_path = f"{user_id}/{image_id}.png"

        try:
            self.location_riddle_repository.write_location_riddle_to_db(user_id, image_id)
        except Exception as e:
            raise BadRequestError(e)

        return self.image_bucket_repository.post_image_to_s3(image_base64, image_path)

    def get_location_riddles_for_user(self, user_id):
        location_riddles = self.location_riddle_repository.get_all_location_riddles()

        response = []
        for location_riddle in location_riddles:
            if location_riddle["user_id"] != user_id:
                continue
            key = f"{user_id}/{location_riddle["location_riddle_id"]}.png"
            location_riddle_image = self.image_bucket_repository.get_image_from_s3(key)
            location_riddle["location_riddle_image"] = location_riddle_image
            response.append(location_riddle)

        if len(location_riddles) == 0:
            raise NotFoundError(f"No location riddles for user with user_id: {user_id} found")
        return response
