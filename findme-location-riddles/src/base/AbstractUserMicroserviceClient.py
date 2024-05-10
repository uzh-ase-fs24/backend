from abc import ABC, abstractmethod


class AbstractUserMicroserviceClient(ABC):

    @abstractmethod
    def get_following_users_list(self, event, username: str):
        pass

    @abstractmethod
    def get_user_scores(self, event, username: str):
        pass

    @abstractmethod
    def write_score_to_user_in_user_db(
            self, event, location_riddle_id: str, score: int
    ):
        pass
