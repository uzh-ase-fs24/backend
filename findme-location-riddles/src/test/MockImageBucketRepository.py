from src.base.AbstractImageBucketRepository import AbstractImageBucketRepository


class MockImageBucketRepository(AbstractImageBucketRepository):
    def __init__(self):
        self.mock_data = {
            "image_base64": "mock_image_base64",
            "Content-Type": "image/png"
        }

    def post_image_to_s3(self, image_base64, key):
        return {"message": "Mock image upload successful"}

    def get_image_from_s3(self, key):
        return self.mock_data

    def delete_image_from_s3(self, key):
        return {"message": "Mock image delete successful"}