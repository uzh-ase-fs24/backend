import unittest
from decimal import Decimal

from ..src.LocationRiddlesService import LocationRiddlesService
from ..src.test.MockImageBucketRepository import MockImageBucketRepository
from ..src.test.MockLocationRiddlesRepository import MockLocationRiddlesRepository
from ..src.test.MockUserMicroserviceClient import MockUserMicroserviceClient


class TestLocationRiddleService(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.image_bucket_repository = MockImageBucketRepository()
        self.location_riddle_repository = MockLocationRiddlesRepository()
        self.user_microservice_client = MockUserMicroserviceClient()
        self.location_riddles_service = LocationRiddlesService(
            self.location_riddle_repository, self.image_bucket_repository, self.user_microservice_client
        )

    def test_post_location_riddle(self):
        self.assertEqual(
            self.location_riddles_service.post_location_riddle(
                "mock_image_base64", [45, 13], ["zurich", "parks"], "mock_username2"
            ),
            {"message": "Mock image upload successful"},
        )

    def test_get_location_riddle(self):
        location_riddle = self.location_riddles_service.get_location_riddle(
            "mock_location_riddle_id", "mock_username"
        )

        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments, [])
        self.assertEqual(location_riddle.image_base64, "mock_image_base64")

    def test_get_location_riddles_for_user(self):
        location_riddles = self.location_riddles_service.get_location_riddles_for_user(
            "mock_username", "mock_requester_username"
        )
        location_riddle = location_riddles[
            0
        ]  # assuming there is at least one location riddle

        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments, [])
        self.assertEqual(location_riddle.image_base64, "mock_image_base64")

    def test_get_solved_location_riddles_for_user(self):
        location_riddles = self.location_riddles_service.get_solved_location_riddles_for_user(
            "event", "mock_username", "mock_username"
        )
        location_riddle = location_riddles[0]

        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.solved, True)

    def test_get_location_riddles_feed(self):
        location_riddles = self.location_riddles_service.get_location_riddles_feed(
            "event", "mock_username"
        )
        location_riddle = location_riddles[0]

        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments, [])
        self.assertEqual(location_riddle.image_base64, "mock_image_base64")

    def test_get_location_riddles_arena(self):
        location_riddles = self.location_riddles_service.get_location_riddles_arena(
            "mock_arena", "mock_username2"
        )
        location_riddle = location_riddles[0]

        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments, [])
        self.assertEqual(location_riddle.image_base64, "mock_image_base64")

        # test retrieving location riddles for an arena that does not exist
        with self.assertRaises(Exception):
            location_riddles = self.location_riddles_service.get_location_riddles_arena(
                "mock_arena2", "mock_username2"
            )

    def test_guess_location_riddle(self):
        # Test that the user can not rate its own location riddle
        with self.assertRaises(Exception):
            self.location_riddles_service.guess_location_riddle(
                "event", "mock_location_riddle_id", "mock_username", [0.0, 0.0]
            )

        # Test that a different user can guess the location riddle
        guess_result = self.location_riddles_service.guess_location_riddle(
            "event", "mock_location_riddle_id", "mock_username2", [0.0, 0.0]
        )
        self.assertEqual(
            guess_result["location_riddle"]["location_riddle_id"],
            "mock_location_riddle_id",
        )
        self.assertEqual(guess_result["location_riddle"]["username"], "mock_username")
        self.assertEqual(guess_result["location_riddle"]["comments"], [])
        self.assertEqual(
            guess_result["location_riddle"]["guesses"][0]["username"], "mock_username2"
        )
        self.assertEqual(guess_result["location_riddle"]["guesses"][0]["guess"]["coordinate"],
                         [Decimal('0.0'), Decimal('0.0')])
        self.assertEqual(guess_result["location_riddle"]["average_rating"], None)
        self.assertEqual(guess_result["guess_result"]["distance"], 0.0)
        self.assertEqual(guess_result["guess_result"]["received_score"], 10000.0)

        # Test that the user can not guess a location riddle twice
        with self.assertRaises(Exception):
            self.location_riddles_service.guess_location_riddle(
                "event", "mock_location_riddle_id", "mock_username2", [0.0, 0.0]
            )

    def test_rate_location_riddle(self):
        # Test that the user can not rate its own location riddle
        with self.assertRaises(Exception):
            self.location_riddles_service.rate_location_riddle(
                "mock_location_riddle_id", "mock_username", 4
            )
        # To be able to see the effect of the rating, we need to have a guess first
        self.location_riddles_service.guess_location_riddle(
            "event", "mock_location_riddle_id", "mock_username2", [0.0, 0.0]
        )
        # Test that a different user can rate the location riddle
        location_riddle = self.location_riddles_service.rate_location_riddle(
            "mock_location_riddle_id", "mock_username2", 3
        )
        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments, [])
        self.assertEqual(location_riddle.average_rating, 3.0)

        # Test that the user can not rate a location riddle twice
        with self.assertRaises(Exception):
            self.location_riddles_service.rate_location_riddle(
                "mock_location_riddle_id", "mock_username2", 6
            )

        # To be able to see the effect of the rating, we need to have a guess first
        self.location_riddles_service.guess_location_riddle(
            "event", "mock_location_riddle_id", "mock_username3", [0.0, 0.0]
        )
        # Test that a third user can rate the location riddle
        location_riddle = self.location_riddles_service.rate_location_riddle(
            "mock_location_riddle_id", "mock_username3", 2
        )
        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments, [])
        self.assertEqual(location_riddle.average_rating, 2.5)

    def test_comment_location_riddle(self):
        location_riddle = self.location_riddles_service.comment_location_riddle(
            "mock_location_riddle_id", "mock_username2", "mock_comment"
        )
        self.assertEqual(location_riddle.location_riddle_id, "mock_location_riddle_id")
        self.assertEqual(location_riddle.username, "mock_username")
        self.assertEqual(location_riddle.comments[0].username, "mock_username2")
        self.assertEqual(location_riddle.comments[0].comment, "mock_comment")

    def test_delete_location_riddle(self):
        self.assertEqual(
            self.location_riddles_service.delete_location_riddle(
                "mock_location_riddle_id", "mock_username"
            ),
            {"message": "Location riddle deleted successfully"},
        )


if __name__ == "__main__":
    unittest.main()
