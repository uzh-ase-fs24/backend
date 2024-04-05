from abc import ABC, abstractmethod


class AbstractDbRepository(ABC):

    @abstractmethod
    def write_location_riddle_to_db(self, id, user_id):
        pass

    @abstractmethod
    def get_all_location_riddles_by_user_id(self, user_id):
        pass

    @abstractmethod
    def get_location_riddle_by_location_riddle_id_from_db(self, location_riddle_id):
        pass

    @abstractmethod
    def delete_location_riddle_from_db(self, location_riddle_id):
        pass