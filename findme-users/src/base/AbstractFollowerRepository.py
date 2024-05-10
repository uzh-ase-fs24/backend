from abc import ABC, abstractmethod


class AbstractFollowerRepository(ABC):
    @abstractmethod
    def accept_follow_request(self, requester: str, requestee: str):
        pass

    @abstractmethod
    def decline_follow_request(self, requester: str, requestee: str):
        pass

    @abstractmethod
    def fetch_received_follow_requests(self, username: str):
        pass

    @abstractmethod
    def fetch_sent_follow_requests(self, username: str):
        pass

    @abstractmethod
    def does_follow_request_exist(self, requester: str, requestee: str):
        pass

    @abstractmethod
    def get_user_connections(self, username: str):
        pass
