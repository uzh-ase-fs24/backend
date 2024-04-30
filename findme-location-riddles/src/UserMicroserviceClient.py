import json
import os
import boto3
from urllib.parse import urljoin
from .base.AbstractUserMicroserviceClient import AbstractUserMicroserviceClient


class UserMicroserviceClient(AbstractUserMicroserviceClient):
    def __init__(self):
        self.client = boto3.client("lambda", region_name="eu-central-2")
        self.base_url = "/users/"

    def get_following_users_list(self, event, username: str):
        event_dict = dict(event)
        event_dict["path"] = urljoin(self.base_url, f"{username}/follow")
        user_connections = self.__invoke_request(event_dict)

        return user_connections["following"]

    def get_user_scores(self, event, username: str):
        event_dict = dict(event)
        event_dict["path"] = urljoin(self.base_url, f"{username}/scores")
        user_scores = self.__invoke_request(event_dict)

        return user_scores

    def write_score_to_user_in_user_db(
        self, event, location_riddle_id: str, score: int
    ):
        event_dict = dict(event)
        event_dict["path"] = urljoin(self.base_url, "score")
        event_dict["body"] = json.dumps(
            {"score": score, "location_riddle_id": location_riddle_id}
        )
        _ = self.__invoke_request(event_dict)

    def __invoke_request(self, event_dict: dict):
        response = self.client.invoke(
            FunctionName=os.environ["USER_FUNCTION_NAME"],
            Payload=json.dumps(event_dict),
        )

        streaming_body = response["Payload"]
        payload_bytes = streaming_body.read()
        payload_str = payload_bytes.decode("utf-8")
        payload_dict = json.loads(payload_str)
        return json.loads(payload_dict["body"])