from src.base.AbstractLocationRiddlesRepository import AbstractLocationRiddlesRepository


class LocationRiddle:

    def __init__(self):
        self.location_riddle_id = "mock_location_riddle_id"
        self.user_id = "mock_user_id"
        self.ratings = []
        self.comments = []
        self.guesses = []
        self.created_at = 1234567890

    def dict(self):
        return {
            "location_riddle_id": self.location_riddle_id,
            "user_id": self.user_id,
            "ratings": self.ratings,
            "comments": self.comments,
            "guesses": self.guesses,
            "created_at": self.created_at
        }


class MockLocationRiddlesRepository(AbstractLocationRiddlesRepository):
    def __init__(self):
        self.mock_data = LocationRiddle()

    def write_location_riddle_to_db(self, user_id, location_riddle_id):
        pass

    def get_all_location_riddles_by_user_id(self, user_id):
        return [self.mock_data]

    def get_location_riddle_by_location_riddle_id_from_db(self, location_riddle_id):
        return self.mock_data

    def delete_location_riddle_from_db(self, location_riddle_id):
        return {"message": "Mock delete successful"}