from pydantic import ValidationError
from src.UserRepository import UserRepository
from src.User import User

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def post_user(self, data):
        try:
            user = User(**data)
        except ValidationError as e:
            print(e)
            return e, 400
        return self.user_repository.post_user_to_db(user)
    
    def get_user(self, userId):
        return self.user_repository.get_user_by_userId_from_db(userId)