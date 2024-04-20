from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
    BadRequestError,
)

from src.entities.User import User, UserDTO
from typing import List


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def post_user(self, data, user_id: str) -> UserDTO:
        return self.user_repository.post_user_to_db({**data, "user_id": user_id}).to_dto()

    def get_user(self, user_id: str) -> UserDTO:
        return self.user_repository.get_user_by_user_id_from_db(user_id).to_dto()

    def update_user(self, data: dict, user_id: str) -> UserDTO:
        return (self.user_repository.update_user_in_db({**data,
                                                        "user_id": user_id,
                                                        "username": self.user_repository
                                                       .get_user_by_user_id_from_db(user_id).username}).to_dto())

    def write_guessing_score_to_user(self, user_id: str, location_riddle_id: str, score: int) -> UserDTO:
        try:
            updated_user = self.user_repository.update_user_score_in_db(
                user_id, location_riddle_id, score
            )
        except Exception as e:
            raise BadRequestError(e)

        return updated_user.to_dto()

    def get_similar_users(self, username_prefix: str, user_id: str) -> List[UserDTO]:
        users = list(filter(lambda user: user.user_id != user_id,
                            self.user_repository
                            .get_users_by_username_prefix(username_prefix)))
        if not users:
            raise NotFoundError(
                f"No users found with username prefix {username_prefix}!"
            )
        return [user.to_dto() for user in users]

    def does_user_with_user_id_exist(self, user_id: str) -> bool:
        return self.user_repository.does_user_with_user_id_exist(user_id)
