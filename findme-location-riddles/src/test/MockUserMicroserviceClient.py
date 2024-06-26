from ..base.AbstractUserMicroserviceClient import AbstractUserMicroserviceClient


class MockUserMicroserviceClient(AbstractUserMicroserviceClient):
    def get_following_users_list(self, event, username: str):
        return [
            {"username": "mock_username", "first_name": "Test", "last_name": "User"},
            {"username": "mock_username2", "first_name": "Test2", "last_name": "User2"}
        ]

    def get_user_scores(self, event, username: str):
        return [
            {"location_riddle_id": "mock_location_riddle_id", "score": 100},
            {"location_riddle_id": "mock_location_riddle_id2", "score": 200}
        ]

    def write_score_to_user_in_user_db(
        self, event, location_riddle_id: str, score: int
    ):
        pass
