from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from pydantic import ValidationError
from src.UserRepository import UserRepository
from src.entities.User import User


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def post_user(self, data, user_id):
        try:
            user_data = {**data, "user_id": user_id}
            user = User(**user_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to create user with provided parameters. {e}")
        self.user_repository.post_user_to_db(user)

        return user

    def get_user(self, user_id):
        return self.user_repository.get_user_by_user_id_from_db(user_id)

    def update_user(self, data, user_id):
        try:
            user_data = {**data, "user_id": user_id, "username": self.user_repository.get_user_by_user_id_from_db(user_id).username}
            user = User(**user_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to update user with provided parameters. {e}")

        self.user_repository.update_user_in_db(user)

        return user

    def get_similar_users(self, username_prefix, user_id):
        user_items = self.user_repository.get_users_by_username_prefix(username_prefix)
        users = []

        for item in user_items:
            # Skip own user
            if item['user_id'] == user_id:
                continue
            try:
                user = User(**item)
                users.append(user)
            except ValidationError as e:
                print(e)
                raise BadRequestError(f"Unable to read Data from DB {e}")

        return users

    def does_user_with_user_id_exist(self, user_id):
        return self.user_repository.does_user_with_user_id_exist(user_id)
