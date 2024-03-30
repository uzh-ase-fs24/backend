from pydantic import ValidationError
from src.UserRepository import UserRepository
from src.User import User
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def post_user(self, data, user_id):
        try:
            user_data = {**data, "user_id": user_id}
            user = User(**user_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to create user with provided parameters. {e}")

        return self.user_repository.post_user_to_db(user)

    def get_user(self, user_id):
        return self.user_repository.get_user_by_user_id_from_db(user_id)

    def update_user(self, data, user_id):
        try:
            user_data = {**data, "user_id": user_id}
            user = User(**user_data)
        except ValidationError as e:
            raise BadRequestError(f"unable to update user with provided parameters. {e}")

        return self.user_repository.update_user_in_db(user)

    def get_similar_users(self, username_prefix):
        user_items = self.user_repository.get_users_by_username_prefix(username_prefix)
        users = []

        for item in user_items:
            try:
                user = User(**item)
                users.append(user)
            except ValidationError as e:
                print(e)
                raise BadRequestError(f"Unable to read Data from DB {e}")

        return users

