from src.base.AbstractLocationRiddlesRepository import AbstractLocationRiddlesRepository


class Rating:
    def __init__(self, user_id: str, rating: int):
        self.user_id = user_id
        self.rating = rating

    def dict(self):
        return {
            "user_id": self.user_id,
            "rating": self.rating
        }


class LocationRiddle:
    def __init__(self):
        self.location_riddle_id = "mock_location_riddle_id"
        self.user_id = "mock_user_id"
        self.ratings = []
        self.comments = []
        self.guesses = []
        self.created_at = 1234567890
        self.average_rating = None

    def dict(self, exclude=set()):
        return {
            attr: value for attr, value in self.__dict__.items() if attr not in exclude
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