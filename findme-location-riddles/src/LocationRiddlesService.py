import uuid
import json
import boto3

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class LocationRiddlesService:
    def __init__(self, location_riddle_repository, image_bucket_repository):
        self.image_bucket_repository = image_bucket_repository
        self.location_riddle_repository = location_riddle_repository

    def post_location_riddle(self, image_base64, user_id):
        location_riddle_id = str(uuid.uuid4())
        image_path = f"location-riddles/{location_riddle_id}.png"

        try:
            self.location_riddle_repository.write_location_riddle_to_db(
                user_id, location_riddle_id
            )
        except Exception as e:
            raise BadRequestError(e)

        return self.image_bucket_repository.post_image_to_s3(image_base64, image_path)

    def get_location_riddle(self, location_riddle_id):
        # TODO: check if requesting user is following the user_id
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        location_riddle_image = self.image_bucket_repository.get_image_from_s3(key)

        return location_riddle.dict() | {"location_riddle_image": location_riddle_image}

    def get_location_riddles_for_user(self, user_id):
        # TODO: check if requesting user is following the user_id
        location_riddles = (
            self.location_riddle_repository.get_all_location_riddles_by_user_id(user_id)
        )
        if len(location_riddles) == 0:
            raise NotFoundError(
                f"No location riddles for user with user_id: {user_id} found"
            )

        response = []
        for location_riddle in location_riddles:
            key = f"location-riddles/{location_riddle.location_riddle_id}.png"
            location_riddle_image = self.image_bucket_repository.get_image_from_s3(key)
            response.append(
                location_riddle.dict()
                | {"location_riddle_image": location_riddle_image}
            )
        return response

    def get_location_riddles_feed(self, event, user_id):
        # TODO: Implement API call to findme-user service to get the list of users that the current user follows
        event_dict = dict(event)
        event_dict["path"] = "/users"
        client = boto3.client("lambda", region_name="eu-central-2")
        response = client.invoke(FunctionName="findme-microservices-local-findme-users", Payload=json.dumps(event_dict))

        streaming_body = response['Payload']
        payload_bytes = streaming_body.read()
        payload_str = payload_bytes.decode('utf-8')
        payload_dict = json.loads(payload_str)

        print(payload_dict)
        # the above code shows a way to call another service to get the list of users that the current user follows.
        # currently set to get /users as the /following endpoint is not implemented in the findme-users service

        following_users = ["660e5fc5de3e93a3b75f51a8", "0FhpaZeIjhSG1lwNR3RWPI20VgLgU5rk@clients"]
        response = []
        for user_id in following_users:
            try:
                response.extend(self.get_location_riddles_for_user(user_id))
            except NotFoundError:
                continue
        return response

    def delete_location_riddle(self, location_riddle_id, user_id):
        location_riddle = self.location_riddle_repository.get_location_riddle_by_location_riddle_id_from_db(
            location_riddle_id
        )

        if location_riddle.user_id != user_id:
            raise BadRequestError("User does not have permission to delete this location riddle")

        key = f"location-riddles/{location_riddle.location_riddle_id}.png"
        self.image_bucket_repository.delete_image_from_s3(key)
        self.location_riddle_repository.delete_location_riddle_from_db(location_riddle_id)
        return {"message": "Location riddle deleted successfully"}