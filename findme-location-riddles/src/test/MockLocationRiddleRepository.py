from src.base.AbstractDbRepository import AbstractDbRepository


class MockLocationRiddleRepository(AbstractDbRepository):
    def __init__(self):
        self.mock_data = {
            "location_riddle_id": "mock_id",
            "user_id": "mock_user_id",
        }

    def write_location_riddle_to_db(self, id, user_id):
        return self.mock_data

    def get_all_location_riddles_by_user_id(self, user_id):
        return [self.mock_data]

    def get_location_riddle_by_location_riddle_id_from_db(self, id):
        return self.mock_data

    def delete_location_riddle_from_db(self, id):
        return {"message": "Mock delete successful"}