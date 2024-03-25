from pydantic import ValidationError
from src.UserRepository import UserRepository
from src.User import User
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def post_user(self, data, userId):
        try:
            user_data = {**data, "userId": userId}
            user = User(**user_data)
            return self.user_repository.post_user_to_db(user)

        except ValidationError as e:
            raise BadRequestError(f"unable to create user with provided parameters. {e}")

    def get_user(self, userId):
        return self.user_repository.get_user_by_userId_from_db(userId)

    def update_user(self, data, userId):
        try:
            # Insert id retrieved from header
            user_data = {**data, "userId": userId}
            user = User(**user_data)
            return self.user_repository.update_user_in_db(user)
        except ValidationError as e:
            raise BadRequestError(f"unable to update user with provided parameters. {e}")
