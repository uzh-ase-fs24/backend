from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
)


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def post_user(self, data, user_id):
        return self.user_repository.post_user_to_db({**data, "user_id": user_id})

    def get_user(self, user_id):
        return self.user_repository.get_user_by_user_id_from_db(user_id)

    def update_user(self, data, user_id):
        return self.user_repository.update_user_in_db({**data,
                                                       "user_id": user_id,
                                                       "username": self.user_repository
                                                      .get_user_by_user_id_from_db(user_id).username})

    def get_similar_users(self, username_prefix, user_id):
        users = self.user_repository.get_users_by_username_prefix(username_prefix)
        if len(users) == 0:
            raise NotFoundError(
                f"No location riddles for user with user_id: {user_id} found"
            )
        return list(filter(lambda user: user.user_id != user_id, users))

    def does_user_with_user_id_exist(self, user_id):
        return self.user_repository.does_user_with_user_id_exist(user_id)
