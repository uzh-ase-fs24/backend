import sys

sys.path.insert(0, "/var/task/.venv/lib/python3.12/site-packages")
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.event_handler.openapi.params import Path
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from typing import List
from enum import Enum
from findme.authorization import Authorizer

from src.UserRepository import UserRepository
from src.FollowerRepository import FollowerRepository
from src.UserService import UserService
from src.FollowerService import FollowerService
from src.entities.UserConnections import UserConnections
from src.entities.FollowRequest import FollowRequest
from src.entities.User import UserDTO, UserPostDTO, UserPutDTO
from src.entities.Score import Score

tracer = Tracer()
logger = Logger()

cors_config = CORSConfig(allow_origin=os.environ.get("FRONTEND_ORIGIN"))
app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)
app.enable_swagger(path="/users/swagger")

authorizer = Authorizer(
    auth0_domain=os.environ.get("AUTH0_DOMAIN"),
    auth0_audience=os.environ.get("AUTH0_AUDIENCE"),
)

user_repository = UserRepository()
user_service = UserService(user_repository)
follower_repository = FollowerRepository()
follower_service = FollowerService(follower_repository)


class RequestBodyAttribute(Enum):
    USERNAME = "username"
    FINDME_USERNAME = "https://findme.ch/username"
    LOCATION_RIDDLE_ID = "location_riddle_id"
    SCORE = "score"
    ACTION = "action"


# TODO Beautify: constructor required for swagger but unused
@app.post("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_user(user: UserPostDTO) -> UserDTO:
    """
    Endpoint: POST /users
    Body: {
                    "first_name": <first_name>,
                    "last_name": "<last_name>",
                }
    Description: Creates a new user in the database.
    Returns: The created user.
    """
    return user_service.post_user(app.current_event.json_body, __get_username())


@app.put("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def update_user(user: UserPutDTO) -> UserDTO:
    """
    Endpoint: PUT /users
    Body: {
                    "first_name": <first_name>,
                    "last_name": "<last_name>"
                }
    Description: Updates an existing user in the database.
    Returns: The result of the user update operation.
    """
    return user_service.update_user(app.current_event.json_body, __get_username())


@app.get("/users/<username>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user(username: Annotated[str, Path()]) -> UserDTO:
    """
    Endpoint: GET /users/<username>
    Body: None
    Description: Retrieves a user from the database by username.
    Returns: The user data.
    """
    return user_service.get_user(username)


@app.get("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_individual_user() -> UserDTO:
    """
    Endpoint: GET /users
    Body: None
    Description: Retrieves the authenticated user's data from the database.
    Returns: The authenticated user's data.
    """
    return user_service.get_user(__get_username())


@app.post("/users/score")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_score_to_user(score: Score) -> UserDTO:
    """
    Endpoint: POST /users/score
    Body: {
        "score": <score_integer>
        "location_riddle_id": <location_riddle_id>
    }
    Description: Write achieved score to the user.
    Returns: The user with the updated score avg.
    """
    return user_service.write_guessing_score_to_user(
        __get_username(),
        __get_attribute_from_request_body(RequestBodyAttribute.LOCATION_RIDDLE_ID.value),
        __get_attribute_from_request_body(RequestBodyAttribute.SCORE.value),
    )


@app.get("/users/search")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_similar_users() -> List[UserDTO]:
    """
    Endpoint: GET /users/search
    Body: None
    Description: Retrieves users from the database whose usernames start with a given prefix.
    Returns: A list of users with similar usernames.
    """
    return user_service.get_similar_users(
        app.current_event.query_string_parameters.get(RequestBodyAttribute.USERNAME.value), __get_username()
    )


@app.get("/users/<username>/scores")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user_scores(username: Annotated[str, Path()]) -> list[Score]:
    """
    Endpoint: GET /users/<username>/scores
    Body: None
    Description: Retrieves all scores of a specific user.
    Returns: A list of scores.
    """
    return user_service.get_user_scores(username)


@app.put("/users/<username>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def follow_user(username: Annotated[str, Path()]) -> FollowRequest:
    """
    Endpoint: PUT /users/{username}/follow
    Body: None
    Description: Send a follow request to the user with the username provided in the path
    Returns: The created FollowRequest with the status 'pending'
    """
    requester = __get_username()
    if not user_service.does_user_with_username_exist(username):
        raise BadRequestError(f"User with username {username} does not exist!")
    return follower_service.create_follower_request(requester, username)


@app.patch("/users/<requester>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def update_follow_user(requester: Annotated[str, Path()]) -> FollowRequest:
    """
    Endpoint: PATCH /users/{username}/follow?action={accept | decline}
    Body: None
    Description: Accept or decline the follow request by the user provided in the path
    Returns: A json confirming the accepting or declining of the follow request
    """
    requestee = __get_username()
    action = app.current_event.query_string_parameters.get(RequestBodyAttribute.ACTION.value)

    if action == "accept":
        return follower_service.accept_follow_request(requester, requestee)
    if action == "decline":
        return follower_service.decline_follow_request(requester, requestee)
    else:
        raise BadRequestError(
            f"Action {action} does not exist, please provide a valid value (accept/decline)"
        )


@app.get("/users/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_received_follow_requests() -> List[FollowRequest]:
    """
    Endpoint: GET /users/follow
    Body: None
    Description: Searches for all pending follow requests based on the user's user token
    Returns: A list of pending FollowRequest objects
    """
    return follower_service.get_received_follow_requests(__get_username())


@app.get("/users/<username>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user_connections(username: Annotated[str, Path()]) -> UserConnections:
    """
    Endpoint: GET /users/username/follow
    Body: None
    Description: Retrieves all connections (followers, following) of a specific user
    Returns:
        Dictionary containing one list for followers and one for following.
        Each list contains of 0-many user objects.
    """
    connections = follower_service.get_user_connections(username)
    followers = (
        [user_service.get_user(follower) for follower in connections.followers]
        if connections.followers
        else []
    )
    following = (
        [user_service.get_user(following) for following in connections.following]
        if connections.following
        else []
    )
    return UserConnections(followers=followers, following=following)


def __get_username():
    return app.context.get("claims").get(RequestBodyAttribute.FINDME_USERNAME.value)


def __get_attribute_from_request_body(attribute: str):
    try:
        return app.current_event.json_body[attribute]
    except KeyError:
        raise BadRequestError(f"Missing attribute {attribute} in request body")


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
