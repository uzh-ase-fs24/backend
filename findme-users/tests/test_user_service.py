import unittest
from aws_lambda_powertools.event_handler.exceptions import NotFoundError, BadRequestError
from pydantic import ValidationError
from unittest.mock import MagicMock, patch

from ..src.UserService import UserService
from ..src.entities.Score import Score
from ..src.entities.User import User, UserDTO, UserPutDTO


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.user_service = UserService(user_repository=self.mock_repo)

    def test_post_user_success(self):
        user_data = {"first_name": "John", "last_name": "Doe", "bio": "Test bio"}
        username = "testuser"
        user = User(username=username, **user_data)
        user_dto = UserDTO(username=username, **user_data)

        self.mock_repo.post_user_to_db.return_value = user

        result = self.user_service.post_user(data=user_data, username=username)

        self.mock_repo.post_user_to_db.assert_called_once_with(user)
        self.assertEqual(result, user_dto)

    def test_post_user_validation_error(self):
        user_data = {"first_name": "John", "bio": "Test bio"}  # Missing last_name
        username = "testuser"
        with self.assertRaises(BadRequestError):
            self.user_service.post_user(data=user_data, username=username)

    def test_get_user(self):
        username = "testuser"
        user = User(username=username, first_name="John", last_name="Doe", bio="Test bio")
        user_dto = user.to_dto()

        self.mock_repo.get_user_by_username_from_db.return_value = user

        result = self.user_service.get_user(username)

        self.mock_repo.get_user_by_username_from_db.assert_called_once_with(username)
        self.assertEqual(result, user_dto)

    def test_update_user_success(self):
        user_data = {"first_name": "Jane", "last_name": "Doe", "bio": "Updated bio"}
        username = "testuser"
        user_put_dto = UserPutDTO(**user_data)
        user = User(username=username, **user_data)
        user_dto = user.to_dto()

        self.mock_repo.update_user_in_db.return_value = user

        result = self.user_service.update_user(data=user_data, username=username)

        self.mock_repo.update_user_in_db.assert_called_once_with(username, user_put_dto)
        self.assertEqual(result, user_dto)

    def test_update_user_validation_error(self):
        user_data = {"first_name": "Jane", "bio": "Updated bio"}  # Missing last_name
        username = "testuser"
        with self.assertRaises(BadRequestError):
            self.user_service.update_user(data=user_data, username=username)

    def test_write_guessing_score_to_user_success(self):
        username = "testuser"
        location_riddle_id = "1"
        score_value = 100
        score = Score(location_riddle_id=location_riddle_id, score=score_value)
        user = User(username=username, first_name="John", last_name="Doe")
        user_dto = user.to_dto()

        self.mock_repo.update_user_score_in_db.return_value = user

        result = self.user_service.write_guessing_score_to_user(username, location_riddle_id, score_value)

        self.mock_repo.update_user_score_in_db.assert_called_once_with(username, score)
        self.assertEqual(result, user_dto)

    def test_write_guessing_score_to_user_validation_error(self):
        with self.assertRaises(BadRequestError):
            self.user_service.write_guessing_score_to_user("testuser", "1", "not-an-int")

    def test_get_similar_users_success(self):
        user_data1 = {"username": "testuser1", "first_name": "John", "last_name": "Doe", "bio": "Test bio"}
        user_data2 = {"username": "testuser2", "first_name": "John", "last_name": "Doe", "bio": "Test bio"}

        similar_users = [User(**user_data1), User(**user_data2)]
        self.mock_repo.get_users_by_username_prefix.return_value = similar_users

        result = self.user_service.get_similar_users(query_username_prefix="test", username=similar_users[0].username)

        self.assertEqual(len(result), 1)
        self.assertNotEqual(result[0].username, similar_users[0].username)

    def test_does_user_with_username_exist(self):
        username = "testuser"
        self.mock_repo.does_user_with_username_exist.return_value = True
        result = self.user_service.does_user_with_username_exist(username)
        self.assertTrue(result)

    def test_write_guessing_score_to_user_exception(self):
        username = "testuser"
        location_riddle_id = "1"
        invalid_score = "not-an-int"  # This is not an integer and should trigger a ValidationError
        with self.assertRaises(BadRequestError) as context:
            self.user_service.write_guessing_score_to_user(username, location_riddle_id, invalid_score)
        self.assertIn("unable to update the user with provided parameters", str(context.exception))

    def test_get_user_scores(self):
        username = "testuser"
        scores = [Score(location_riddle_id="1", score=10), Score(location_riddle_id="2", score=20)]
        user = User(username=username, first_name="John", last_name="Doe", scores=scores)

        self.mock_repo.get_user_by_username_from_db.return_value = user

        result = self.user_service.get_user_scores(username)

        self.mock_repo.get_user_by_username_from_db.assert_called_once_with(username)
        self.assertEqual(result, scores)


if __name__ == "__main__":
    unittest.main()
