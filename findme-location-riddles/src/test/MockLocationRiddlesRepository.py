from ..entities.Coordinate import Coordinate
from ..base.AbstractLocationRiddlesRepository import AbstractLocationRiddlesRepository
from ..entities.Comment import Comment
from ..entities.Guess import Guess
from ..entities.LocationRiddle import LocationRiddle
from ..entities.Rating import Rating


class MockLocationRiddlesRepository(AbstractLocationRiddlesRepository):
    def __init__(self):
        self.mock_data = [
            LocationRiddle(
                location_riddle_id="mock_location_riddle_id",
                username="mock_username",
                location=Coordinate(coordinate=[0.0, 0.0]),
                arenas=["mock_arena"],
            )
        ]

    def write_location_riddle_to_db(self, location_riddle: LocationRiddle):
        self.mock_data.append(location_riddle)

    def get_all_location_riddles_by_username(self, username: str):
        return [mock_data for mock_data in self.mock_data if mock_data.username == username]

    def get_location_riddle_by_location_riddle_id_from_db(
        self, location_riddle_id: str
    ):
        for mock_data in self.mock_data:
            if mock_data.location_riddle_id == location_riddle_id:
                return mock_data
        raise Exception("Location riddle not found")

    def get_all_location_riddles_containing_arena(self, arena: str):
        return [mock_data for mock_data in self.mock_data if arena in mock_data.arenas]

    def update_location_riddle_rating_in_db(
        self, location_riddle_id: str, rating: Rating
    ):
        mock_data = self.get_location_riddle_by_location_riddle_id_from_db(location_riddle_id).dict()
        mock_data["ratings"].append(rating)
        updated_location_riddle = LocationRiddle(**mock_data)
        self.mock_data = [updated_location_riddle]
        return updated_location_riddle

    def update_location_riddle_comments_in_db(
        self, location_riddle_id: str, comment: Comment
    ):
        mock_data = self.get_location_riddle_by_location_riddle_id_from_db(location_riddle_id).dict()
        mock_data["comments"].append(comment)
        updated_location_riddle = LocationRiddle(**mock_data)
        self.mock_data = [updated_location_riddle]
        return updated_location_riddle

    def update_location_riddle_guesses_in_db(
        self, location_riddle_id: str, guess: Guess
    ):
        mock_data = self.get_location_riddle_by_location_riddle_id_from_db(location_riddle_id).dict()
        mock_data["guesses"].append(guess)
        updated_location_riddle = LocationRiddle(**mock_data)
        self.mock_data = [updated_location_riddle]
        return updated_location_riddle

    def delete_location_riddle_from_db(self, location_riddle_id: str):
        return {"message": "Mock delete successful"}
