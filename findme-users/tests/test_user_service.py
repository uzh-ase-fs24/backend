import unittest

from ..src.UserService import UserService
from ..src.test.MockUserRepository import MockUserRepository


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_repository = MockUserRepository()
        self.user_service = UserService(self.user_repository)

    def test_post_user(self):
        # Test correct input
        user_data = {"first_name": "Test", "last_name": "User", "bio": "Test bio"}
        username = "testuser"
        result = self.user_service.post_user(user_data, username)
        self.assertEqual(result.username, "testuser")
        self.assertEqual(result.first_name, "Test")
        self.assertEqual(result.last_name, "User")
        self.assertEqual(result.bio, "Test bio")

        # Test incorrect input (same username)
        user_data = {
            "first_name": "Test",
            "last_name": "User",
        }
        username = "testuser"
        with self.assertRaises(ValueError):
            self.user_service.post_user(user_data, username)

    def test_get_user(self):
        # Create a user
        user_data = {"first_name": "Test", "last_name": "User"}
        username = "testuser"
        _ = self.user_service.post_user(user_data, username)

        # Test correct input
        username = "testuser"
        result = self.user_service.get_user(username)
        self.assertEqual(result.last_name, "User")

        # Test incorrect input
        username = "not_existing"
        with self.assertRaises(ValueError):
            self.user_service.get_user(username)

    def test_get_user_scores(self):
        # Create a user
        user_data = {"first_name": "Test", "last_name": "User"}
        username = "testuser"
        _ = self.user_service.post_user(user_data, username)

        # Test correct input
        username = "testuser"
        result = self.user_service.get_user_scores(username)
        self.assertEqual(result, [])

        # add a score to the user
        location_riddle_id = "test_location_riddle_id"
        score = 10
        _ = self.user_service.write_guessing_score_to_user(username, location_riddle_id, score)
        result = self.user_service.get_user_scores(username)
        self.assertEqual(result[0].location_riddle_id, location_riddle_id)

    def test_update_user(self):
        # Create a user
        user_data = {"first_name": "Test", "last_name": "User"}
        username = "testuser"
        _ = self.user_service.post_user(user_data, username)

        # Test correct input
        user_data = {"first_name": "Updated", "last_name": "User"}
        username = "testuser"
        result = self.user_service.update_user(user_data, username)
        self.assertEqual(result.first_name, "Updated")

        # Test incorrect input
        username = "non_existing"
        with self.assertRaises(ValueError):
            self.user_service.update_user(user_data, username)

    def test_get_similar_users(self):
        # Create users
        user_data = {"first_name": "John", "last_name": "Doe"}
        username = "johndoe"
        _ = self.user_service.post_user(user_data, username)
        user_data = {"username": "janedoe", "first_name": "Jane", "last_name": "Doe"}
        username = "janedoe"
        _ = self.user_service.post_user(user_data, username)
        user_data = {"first_name": "jack", "last_name": "Doe"}
        username = "jackdoe"
        _ = self.user_service.post_user(user_data, username)

        # Test correct input
        username_prefix = "j"
        username = "johndoe"
        self.assertEqual(
            len(self.user_service.get_similar_users(username_prefix, username)), 2
        )
        username_prefix = "jane"
        result = self.user_service.get_similar_users(username_prefix, username)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].last_name, "Doe")

        # Test incorrect input
        username_prefix = "non_exisiting"
        with self.assertRaises(Exception):
            self.user_service.get_similar_users(username_prefix, username)

    def test_does_user_with_username_exist(self):
        user_data = {"first_name": "Test", "last_name": "User"}
        username = "testuser"
        _ = self.user_service.post_user(user_data, username)
        # Test correct input
        username = "testuser"
        result = self.user_service.does_user_with_username_exist(username)
        self.assertTrue(result)

        # Test incorrect input
        username = "non_existing"
        result = self.user_service.does_user_with_username_exist(username)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
