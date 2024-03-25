from pydantic import ValidationError
from src.UserRepository import UserRepository
from src.UserDto import UserDto
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def post_user(self, data):
        try:
            user = UserDto(**data)
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(f"unable to create user with provided parameters. {e}")
        return self.user_repository.post_user_to_db(user)
    
    def get_user(self, userId):
        return self.user_repository.get_user_by_userId_from_db(userId)