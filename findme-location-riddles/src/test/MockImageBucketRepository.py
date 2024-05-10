from ..base.AbstractImageBucketRepository import AbstractImageBucketRepository


class MockImageBucketRepository(AbstractImageBucketRepository):
    def __init__(self):
        self.mock_data = "mock_image_base64"

    def post_image_to_s3(self, image_base64: str, key: str):
        return {"message": "Mock image upload successful"}

    def get_image_from_s3(self, key: str):
        return self.mock_data

    def delete_image_from_s3(self, key: str):
        return {"message": "Mock image delete successful"}
