import unittest
# from src.LocationRiddlesService import LocationRiddlesService
from src.test.MockImageBucketRepository import MockImageBucketRepository
from src.test.MockLocationRiddleRepository import MockLocationRiddleRepository

class TestLocationRiddleService(unittest.TestCase):
    def setUp(self):
        self.image_bucket_repository = MockImageBucketRepository()
        self.location_riddle_repository = MockLocationRiddleRepository()
        # self.location_riddles_service = LocationRiddlesService(self.location_riddle_repository, self.image_bucket_repository)

    def test_post_image_to_s3(self):
        self.assertEqual(self.image_bucket_repository.post_image_to_s3("image", "key"),
                         {"message": "Mock image upload successful"})


    def test_get_image_from_s3(self):
        self.assertEqual(self.image_bucket_repository.get_image_from_s3("key"),
                         {
                             "image_base64": "mock_image_base64",
                             "Content-Type": "image/png"
                         })


if __name__ == '__main__':
    unittest.main()