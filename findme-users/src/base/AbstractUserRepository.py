from abc import ABC, abstractmethod


class AbstractUserRepository(ABC):

    @abstractmethod
    def post_user_to_db(self, user_data):
        pass

    @abstractmethod
    def update_user_in_db(self, user_data):
        pass

    @abstractmethod
    def get_user_by_user_id_from_db(self, user_id):
        pass

    @abstractmethod
    def get_users_by_username_prefix(self, username_prefix):
        pass

    @abstractmethod
    def does_user_with_user_id_exist(self, user_id):
        pass
