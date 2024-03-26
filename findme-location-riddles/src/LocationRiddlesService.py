from src.ImageRepository import ImageRepository


class LocationRiddlesService:
    def __init__(self):
        self.image_repository = ImageRepository()

    def post_image(self, image_base64, user_id):
        return self.image_repository.post_image_to_s3(image_base64, user_id)

    def get_image(self, user_id):
        return self.image_repository.get_image_from_s3(user_id)
