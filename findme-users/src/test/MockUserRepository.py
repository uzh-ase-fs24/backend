from ..base.AbstractUserRepository import AbstractUserRepository


class MockUserRepository(AbstractUserRepository):
    def __init__(self):
        self.users = []

    def post_user_to_db(self, user):
        if self.does_user_with_username_exist(user.username):
            raise ValueError(f"Username '{user.username}' is already taken!")
        self.users.append(user)
        return user

    def update_user_in_db(self, username, user_put_dto):
        for i, u in enumerate(self.users):
            if u.username == username:
                self.users[i].first_name = user_put_dto.first_name
                self.users[i].last_name = user_put_dto.last_name
                return self.users[i]
        raise ValueError(f"No User with username: {username} found")

    def get_user_by_username_from_db(self, username):
        for user in self.users:
            if user.username == username:
                return user
        raise ValueError(f"No User with username: {username} found")

    def get_users_by_username_prefix(self, username_prefix):
        return [
            user for user in self.users if user.username.startswith(username_prefix)
        ]

    def update_user_score_in_db(self, username, score):
        for i, user in enumerate(self.users):
            if user.username == username:
                self.users[i].scores.append(score)
                return self.users[i]
        raise ValueError(f"No User with username: {username} found")

    def does_user_with_username_exist(self, username):
        return any(user.username == username for user in self.users)
