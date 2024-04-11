from abc import ABC, abstractmethod
from typing import List
from src.entities.User import User

class AbstractUserRepository(ABC):

    @abstractmethod
    def post_user_to_db(self, user: User):
        pass

    @abstractmethod
    def update_user_in_db(self, user: User):
        pass

    @abstractmethod
    def get_user_by_user_id_from_db(self, user_id: str) -> User:
        pass

    @abstractmethod
    def get_users_by_username_prefix(self, username_prefix: str) -> List[User]:
        pass

    @abstractmethod
    def does_user_with_user_id_exist(self, user_id: str) -> bool:
        pass
