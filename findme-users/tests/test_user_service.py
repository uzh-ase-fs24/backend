import unittest

from ..src.UserService import UserService
from ..src.test.MockUserRepository import MockUserRepository


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_repository = MockUserRepository()
        self.user_service = UserService(self.user_repository)

    def test_post_user(self):
        # Test correct input
        user_data = {"username": "testuser", "first_name": "Test", "last_name": "User"}
        user_id = "1"
        result = self.user_service.post_user(user_data, user_id)
        self.assertEqual(result.username, "testuser")
        self.assertEqual(result.first_name, "Test")
        self.assertEqual(result.last_name, "User")
        self.assertEqual(result.user_id, "1")

        # Test incorrect input
        user_data = {
            "username": "testuser_2",
            "first_name": "Test",
            "last_name": "User",
        }
        user_id = "1"
        with self.assertRaises(ValueError):
            self.user_service.post_user(user_data, user_id)
        user_data = {"username": "testuser", "first_name": "Test", "last_name": "User"}
        user_id = "2"
        with self.assertRaises(ValueError):
            self.user_service.post_user(user_data, user_id)

    def test_get_user(self):
        # Create a user
        user_data = {"username": "testuser", "first_name": "Test", "last_name": "User"}
        user_id = "1"
        _ = self.user_service.post_user(user_data, user_id)

        # Test correct input
        user_id = "1"
        result = self.user_service.get_user(user_id)
        self.assertEqual(result.user_id, "1")

        # Test incorrect input
        user_id = "2"
        with self.assertRaises(ValueError):
            self.user_service.get_user(user_id)

    def test_update_user(self):
        # Create a user
        user_data = {"username": "testuser", "first_name": "Test", "last_name": "User"}
        user_id = "1"
        _ = self.user_service.post_user(user_data, user_id)

        # Test correct input
        user_data = {"first_name": "Updated", "last_name": "User"}
        user_id = "1"
        result = self.user_service.update_user(user_data, user_id)
        self.assertEqual(result.first_name, "Updated")

        # Test incorrect input
        user_id = "2"
        with self.assertRaises(ValueError):
            self.user_service.update_user(user_data, user_id)

    def test_get_similar_users(self):
        # Create users
        user_data = {"username": "johndoe", "first_name": "John", "last_name": "Doe"}
        user_id = "1"
        _ = self.user_service.post_user(user_data, user_id)
        user_data = {"username": "janedoe", "first_name": "Jane", "last_name": "Doe"}
        user_id = "2"
        _ = self.user_service.post_user(user_data, user_id)
        user_data = {"username": "jackdoe", "first_name": "jack", "last_name": "Doe"}
        user_id = "3"
        _ = self.user_service.post_user(user_data, user_id)

        # Test correct input
        username_prefix = "j"
        user_id = "1"
        self.assertEqual(
            len(self.user_service.get_similar_users(username_prefix, user_id)), 2
        )
        username_prefix = "jane"
        result = self.user_service.get_similar_users(username_prefix, user_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, "janedoe")

        # Test incorrect input
        username_prefix = "nonexistent"
        with self.assertRaises(Exception):
            self.user_service.get_similar_users(username_prefix, user_id)

    def test_does_user_with_user_id_exist(self):
        user_data = {"username": "testuser", "first_name": "Test", "last_name": "User"}
        user_id = "1"
        _ = self.user_service.post_user(user_data, user_id)
        # Test correct input
        user_id = "1"
        result = self.user_service.does_user_with_user_id_exist(user_id)
        self.assertTrue(result)

        # Test incorrect input
        user_id = "2"
        result = self.user_service.does_user_with_user_id_exist(user_id)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
