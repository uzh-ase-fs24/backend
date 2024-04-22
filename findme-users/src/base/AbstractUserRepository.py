from abc import ABC, abstractmethod

from ..entities.User import User, UserPutDTO


class AbstractUserRepository(ABC):

    @abstractmethod
    def post_user_to_db(self, user_data: User):
        pass

    @abstractmethod
    def update_user_in_db(self, user_id: str, user_data: UserPutDTO):
        pass

    @abstractmethod
    def get_user_by_user_id_from_db(self, user_id: str):
        pass

    @abstractmethod
    def get_users_by_username_prefix(self, username_prefix: str):
        pass

    @abstractmethod
    def update_user_score_in_db(self, user_id: str, location_riddle_id: str, score: int):
        pass

    @abstractmethod
    def does_user_with_user_id_exist(self, user_id: str):
        pass
