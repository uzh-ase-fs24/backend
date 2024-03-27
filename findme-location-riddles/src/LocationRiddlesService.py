from src.ImageBucketRepository import ImageBucketRepository
from src.ImageDbRepository import ImageDbRepository
import uuid
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)

class LocationRiddlesService:
    def __init__(self):
        self.image_bucket_repository = ImageBucketRepository()
        self.image_db_repository = ImageDbRepository()

    def post_image(self, image_base64, user_id):
        image_id = str(uuid.uuid4())
        image_path = f"{user_id}/{image_id}.png"

        try:
            self.image_db_repository.write_image_to_db(user_id, image_id)
        except Exception as e:
            raise BadRequestError(e)

        return self.image_bucket_repository.post_image_to_s3(image_base64, image_path)

    def get_image(self, user_id):
        return self.image_bucket_repository.get_image_from_s3(user_id)
