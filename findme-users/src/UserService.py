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

    def post_user(self, data, user_id: str) -> UserDTO:
        try:
            user = User(**{**data, "user_id": user_id})
        except ValidationError as e:
            print(f"unable to create user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to create user with provided parameters. {e}"
            )

        return self.user_repository.post_user_to_db(user).to_dto()

    def get_user(self, user_id: str) -> UserDTO:
        return self.user_repository.get_user_by_user_id_from_db(user_id).to_dto()

    def update_user(self, data: dict, user_id: str) -> UserDTO:
        try:
            user_put_dto = UserPutDTO(**data)
        except ValidationError as e:
            print(f"unable to update user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to update user with provided parameters. {e}"
            )
        return self.user_repository.update_user_in_db(user_id, user_put_dto).to_dto()

    def write_guessing_score_to_user(
        self, user_id: str, location_riddle_id: str, score: int
    ) -> UserDTO:
        try:
            score = Score(location_riddle_id=location_riddle_id, score=score)
        except ValidationError as e:
            print(f"unable to update the user with provided parameters. {e}")
            raise BadRequestError(
                f"unable to update the user with provided parameters. {e}"
            )

        try:
            updated_user = self.user_repository.update_user_score_in_db(user_id, score)
        except Exception as e:
            print(e)
            raise BadRequestError(e)

        return updated_user.to_dto()

    def get_similar_users(self, username_prefix: str, user_id: str) -> List[UserDTO]:
        users = list(
            filter(
                lambda user: user.user_id != user_id,
                self.user_repository.get_users_by_username_prefix(username_prefix),
            )
        )
        if not users:
            raise NotFoundError(
                f"No users found with username prefix {username_prefix}!"
            )
        return [user.to_dto() for user in users]

    def does_user_with_user_id_exist(self, user_id: str) -> bool:
        return self.user_repository.does_user_with_user_id_exist(user_id)
