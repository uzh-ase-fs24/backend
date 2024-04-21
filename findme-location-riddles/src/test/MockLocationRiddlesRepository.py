from src.base.AbstractLocationRiddlesRepository import AbstractLocationRiddlesRepository
from src.entities.Rating import Rating
from src.entities.Comment import Comment
from src.entities.Guess import Guess
from src.entities.LocationRiddle import LocationRiddle


class MockLocationRiddlesRepository(AbstractLocationRiddlesRepository):
    def __init__(self):
        self.mock_data = LocationRiddle(
            **{
                "location_riddle_id": "mock_location_riddle_id",
                "user_id": "mock_user_id",
                "location": [0.0, 0.0]
            }
        )

    def write_location_riddle_to_db(self, location_riddle: LocationRiddle):
        self.mock_data = location_riddle

    def get_all_location_riddles_by_user_id(self, user_id: str):
        return [self.mock_data]

    def get_location_riddle_by_location_riddle_id_from_db(self, location_riddle_id: str):
        return self.mock_data

    def update_location_riddle_rating_in_db(self, location_riddle_id: str, rating: Rating):
        mock_data = self.mock_data.dict()
        mock_data["ratings"].append(rating)
        self.mock_data = LocationRiddle(**mock_data)
        return self.mock_data

    def update_location_riddle_comments_in_db(self, location_riddle_id: str, comment: Comment):
        mock_data = self.mock_data.dict()
        mock_data["comments"].append(comment)
        self.mock_data = LocationRiddle(**mock_data)
        return self.mock_data

    def update_location_riddle_guesses_in_db(self, location_riddle_id: str, guess: Guess):
        mock_data = self.mock_data.dict()
        mock_data["guesses"].append(guess)
        self.mock_data = LocationRiddle(**mock_data)
        return self.mock_data

    def delete_location_riddle_from_db(self, location_riddle_id: str):
        return {"message": "Mock delete successful"}