from abc import ABC, abstractmethod

from ..entities.User import User, UserPutDTO


class AbstractUserRepository(ABC):
    @abstractmethod
    def post_user_to_db(self, user_data: User):
        pass

    @abstractmethod
    def update_user_in_db(self, username: str, user_data: UserPutDTO):
        pass

    @abstractmethod
    def get_user_by_username_from_db(self, username: str):
        pass

    @abstractmethod
    def get_users_by_username_prefix(self, username_prefix: str):
        pass

    @abstractmethod
    def update_user_score_in_db(self, username: str, score: int):
        pass
