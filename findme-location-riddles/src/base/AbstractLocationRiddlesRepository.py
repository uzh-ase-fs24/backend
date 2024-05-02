from abc import ABC, abstractmethod

from ..entities.Comment import Comment
from ..entities.Guess import Guess
from ..entities.LocationRiddle import LocationRiddle
from ..entities.Rating import Rating


class AbstractLocationRiddlesRepository(ABC):
    @abstractmethod
    def write_location_riddle_to_db(self, location_riddle: LocationRiddle):
        pass

    @abstractmethod
    def get_all_location_riddles_by_username(self, username: str):
        pass

    @abstractmethod
    def get_location_riddle_by_location_riddle_id_from_db(
        self, location_riddle_id: str
    ):
        pass

    @abstractmethod
    def get_all_location_riddles_containing_arena(self, arena: str):
        pass

    @abstractmethod
    def update_location_riddle_rating_in_db(
        self, location_riddle_id: str, rating: Rating
    ):
        pass

    @abstractmethod
    def update_location_riddle_comments_in_db(
        self, location_riddle_id: str, comment: Comment
    ):
        pass

    @abstractmethod
    def update_location_riddle_guesses_in_db(
        self, location_riddle_id: str, guess: Guess
    ):
        pass

    @abstractmethod
    def delete_location_riddle_from_db(self, location_riddle_id: str):
        pass
