from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
    BadRequestError,
)
from pydantic import ValidationError
from typing import List

from .entities.Score import Score
from .entities.User import User, UserDTO, UserPutDTO


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def post_user(self, data, username: str) -> UserDTO:
        try:
            user = User(**{**data, "username": username})
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to create user with provided parameters. {e}"
            )

        return self.user_repository.post_user_to_db(user).to_dto()

    def get_user(self, username: str) -> UserDTO:
        return self.user_repository.get_user_by_username_from_db(username).to_dto()

    def update_user(self, data: dict, username: str) -> UserDTO:
        try:
            user_put_dto = UserPutDTO(**data)
        except ValidationError as e:
            print(f"unable to update user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to update user with provided parameters. {e}"
            )
        return self.user_repository.update_user_in_db(username, user_put_dto).to_dto()

    def write_guessing_score_to_user(
        self, username: str, location_riddle_id: str, score: int
    ) -> UserDTO:
        try:
            score = Score(location_riddle_id=location_riddle_id, score=score)
        except ValidationError as e:
            print(f"unable to update the user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to update the user with provided parameters. {e}"
            )

        try:
            updated_user = self.user_repository.update_user_score_in_db(username, score)
        except Exception as e:
            print(e)
            raise BadRequestError(e)

        return updated_user.to_dto()

    def get_similar_users(
        self, query_username_prefix: str, username: str
    ) -> List[UserDTO]:
        users = list(
            filter(
                lambda user: user.username != username,
                self.user_repository.get_users_by_username_prefix(
                    query_username_prefix
                ),
            )
        )
        if not users:
            raise NotFoundError(
                f"No users found with username prefix {query_username_prefix}!"
            )
        return [user.to_dto() for user in users]

    def does_user_with_username_exist(self, username: str) -> bool:
        return self.user_repository.does_user_with_username_exist(username)
