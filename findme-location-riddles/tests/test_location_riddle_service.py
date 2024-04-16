import unittest
from src.LocationRiddlesService import LocationRiddlesService
from src.test.MockImageBucketRepository import MockImageBucketRepository
from src.test.MockLocationRiddlesRepository import MockLocationRiddlesRepository


class TestLocationRiddleService(unittest.TestCase):
    def setUp(self):
        self.image_bucket_repository = MockImageBucketRepository()
        self.location_riddle_repository = MockLocationRiddlesRepository()
        self.location_riddles_service = LocationRiddlesService(self.location_riddle_repository, self.image_bucket_repository)

    def test_post_location_riddle(self):
        self.assertEqual(self.location_riddles_service.post_location_riddle("mock_image_base64",
                                                                            "mock_user_id",
                                                                            [0.0, 0.0]),
                         {"message": "Mock image upload successful"})

    def test_get_location_riddle(self):
        self.assertEqual(self.location_riddles_service.get_location_riddle("mock_location_riddle_id"),
                         {
                             "location_riddle_id": "mock_location_riddle_id",
                             "user_id": "mock_user_id", "location": [0.0, 0.0], "comments": [],
                             "guesses": [], "created_at": 1234567890, "average_rating": None,
                             "location_riddle_image": {"image_base64": "mock_image_base64",
                                                       "Content-Type": "image/png"}
                         })

    def test_get_location_riddles_for_user(self):
        self.assertEqual(self.location_riddles_service.get_location_riddles_for_user("mock_user_id"),
                         [{
                             "location_riddle_id": "mock_location_riddle_id",
                             "user_id": "mock_user_id",  "location": [0.0, 0.0], "comments": [],
                             "guesses": [], "created_at": 1234567890, "average_rating": None,
                             "location_riddle_image": {"image_base64": "mock_image_base64",
                                                       "Content-Type": "image/png"}
                         }])

    def test_rate_location_riddle(self):
        # Test that the user can not rate its own location riddle
        with self.assertRaises(Exception):
            self.location_riddles_service.rate_location_riddle("mock_location_riddle_id",
                                                              "mock_user_id", 6)

        self.assertEqual(self.location_riddles_service.rate_location_riddle("mock_location_riddle_id",
                                                                            "mock_user2_id", 3),
                         {
                             "location_riddle_id": "mock_location_riddle_id",
                             "user_id": "mock_user_id",  "location": [0.0, 0.0], "comments": [],
                             "guesses": [], "created_at": 1234567890, "average_rating": 3
                         })

        # Test that the user can not rate a location riddle twice
        with self.assertRaises(Exception):
            self.location_riddles_service.rate_location_riddle("mock_location_riddle_id",
                                                              "mock_user2_id", 6)

        self.assertEqual(self.location_riddles_service.rate_location_riddle("mock_location_riddle_id",
                                                                            "mock_user3_id", 2),
                         {
                             "location_riddle_id": "mock_location_riddle_id",
                             "user_id": "mock_user_id",  "location": [0.0, 0.0], "comments": [],
                             "guesses": [], "created_at": 1234567890, "average_rating": 2.5
                         })


    def test_delete_location_riddle(self):
        self.assertEqual(self.location_riddles_service.delete_location_riddle("mock_location_riddle_id", "mock_user_id"),
                         {"message": "Location riddle deleted successfully"})


if __name__ == '__main__':
    unittest.main()