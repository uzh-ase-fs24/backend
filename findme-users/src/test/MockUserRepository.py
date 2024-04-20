from src.base.AbstractUserRepository import AbstractUserRepository


class User:
    def __init__(self, user_id, username, first_name, last_name):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def dict(self, exclude=set()):
        return {
            attr:
                [item.dict() if hasattr(item, 'dict') and callable(item.dict) else item for item in value]
                if isinstance(value, list)
                else value.dict()
                if hasattr(value, 'dict') and callable(value.dict)
                else value
            for attr, value in self.__dict__.items()
            if attr not in exclude
        }


class MockUserRepository(AbstractUserRepository):
    def __init__(self):
        self.users = []

    def post_user_to_db(self, user_data):
        user = User(**user_data)
        if self.does_user_with_user_id_exist(user.user_id):
            raise ValueError(f"User with id {user.user_id} already has an account!")
        if self.__does_user_with_username_exist(user.username):
            raise ValueError(f"Username '{user.username}' is already taken!")
        self.users.append(user)
        return user

    def update_user_in_db(self, user_data):
        user = User(**user_data)
        for i, u in enumerate(self.users):
            if u.user_id == user.user_id:
                self.users[i] = user
                return user
        raise ValueError(f"No User with user_id: {user.user_id} found")

    def get_user_by_user_id_from_db(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                return user
        raise ValueError(f"No User with user_id: {user_id} found")

    def get_users_by_username_prefix(self, username_prefix):
        return [user for user in self.users if user.username.startswith(username_prefix)]

    def does_user_with_user_id_exist(self, user_id):
        return any(user.user_id == user_id for user in self.users)

    def __does_user_with_username_exist(self, username):
        return any(user.username == username for user in self.users)