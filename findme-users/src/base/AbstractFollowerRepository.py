from abc import ABC, abstractmethod

class AbstractFollowerRepository(ABC):

    @abstractmethod
    def accept_follow_request(self, requester_id: str, requestee_id: str):
        pass

    @abstractmethod
    def decline_follow_request(self, requester_id: str, requestee_id: str):
        pass

    @abstractmethod
    def fetch_received_follow_requests(self, user_id: str):
        pass

    @abstractmethod
    def fetch_sent_follow_requests(self, user_id: str):
        pass

    @abstractmethod
    def does_follow_request_exist(self, requester_id, requestee_id):
        pass

    @abstractmethod
    def get_following(self, user_id: str):
        pass

    @abstractmethod
    def get_followers(self, user_id: str):
        pass