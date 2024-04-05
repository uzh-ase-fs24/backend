import unittest
from src.LocationRiddlesService import LocationRiddlesService
from src.test.MockImageBucketRepository import MockImageBucketRepository
from src.test.MockLocationRiddleRepository import MockLocationRiddleRepository


class TestLocationRiddleService(unittest.TestCase):
    def setUp(self):
        self.image_bucket_repository = MockImageBucketRepository()
        self.location_riddle_repository = MockLocationRiddleRepository()
        self.location_riddles_service = LocationRiddlesService(self.location_riddle_repository, self.image_bucket_repository)

    def test_post_location_riddle(self):
        self.assertEqual(self.location_riddles_service.post_location_riddle("mock_image_base64", "mock_user_id"),
                         {"message": "Mock image upload successful"})


if __name__ == '__main__':
    unittest.main()