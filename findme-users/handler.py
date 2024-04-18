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

from findme.authorization import Authorizer

from src.UserRepository import UserRepository
from src.FollowerRepository import FollowerRepository
from src.UserService import UserService
from src.FollowerService import FollowerService
from src.entities.UserConnections import UserConnections


tracer = Tracer()
logger = Logger()

cors_config = CORSConfig(allow_origin=os.environ.get("FRONTEND_ORIGIN"))
app = APIGatewayRestResolver(cors=cors_config)

authorizer = Authorizer(
    auth0_domain=os.environ.get("AUTH0_DOMAIN"),
    auth0_audience=os.environ.get("AUTH0_AUDIENCE"),
)

user_repository = UserRepository()
user_service = UserService(user_repository)
follower_repository = FollowerRepository()
follower_service = FollowerService(follower_repository)


@app.post("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_user():
    """
        Endpoint: POST /users
        Body: {
                        "first_name": <first_name>,
                        "last_name": "<last_name>",
                        "username": <username>
                    }
        Description: Creates a new user in the database.
        Returns: The created user including the user_id.
    """
    return user_service.post_user(app.current_event.json_body, __get_id(app))


@app.put("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def update_user():
    """
        Endpoint: PUT /users
        Body: {
                        "first_name": <first_name>,
                        "last_name": "<last_name>"
                    }
        Description: Updates an existing user in the database.
        Returns: The result of the user update operation.
    """
    return user_service.update_user(app.current_event.json_body, __get_id(app))


@app.get("/users/<user_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user(user_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: GET /users/<user_id>
        Body: None
        Description: Retrieves a user from the database by user_id.
        Returns: The user data.
    """
    return user_service.get_user(user_id)


@app.get("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_individual_user():
    """
        Endpoint: GET /users
        Body: None
        Description: Retrieves the authenticated user's data from the database.
        Returns: The authenticated user's data.
    """
    return user_service.get_user(__get_id(app))


@app.get("/users/search")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_similar_users():
    """
        Endpoint: GET /users/search
        Body: None
        Description: Retrieves users from the database whose usernames start with a given prefix.
        Returns: A list of users with similar usernames.
    """
    return user_service.get_similar_users(
        app.current_event.query_string_parameters.get("username"),
        __get_id(app))


@app.put("/users/<user_id>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def follow_user(user_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: PUT /users/{user_id}/follow
        Body: None
        Description: Send a follow request to the user with the ID provided in the path
        Returns: The created FollowRequest with the status 'pending'
    """
    requester_id = __get_id(app)
    if not user_service.does_user_with_user_id_exist(user_id):
        raise BadRequestError(f"User with user id {user_id} does not exist!")
    # TODO Not so nice
    requester_username = user_service.get_user(requester_id).username
    return follower_service.create_follower_request(requester_username, requester_id, user_id)


@app.patch("/users/<requester_id>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def update_follow_user(requester_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: PATCH /users/{user_id}/follow?action={accept | decline}
        Body: None
        Description: Accept or decline the follow request by the user provided in the path
        Returns: A json confirming the accepting or declining of the follow request
    """
    requestee_id = __get_id(app)
    action = app.current_event.query_string_parameters.get("action")

    if action == "accept":
        return follower_service.accept_follow_request(requester_id, requestee_id)
    if action == "decline":
        return follower_service.decline_follow_request(requester_id, requestee_id)
    else:
        raise BadRequestError(f"Action {action} does not exist, please provide a valid value (accept/decline)")


@app.get("/users/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_received_follow_requests():
    """
        Endpoint: GET /users/follow
        Body: None
        Description: Searches for all pending follow requests based on the user's user token
        Returns: A list of pending FollowRequest objects
    """
    return follower_service.get_received_follow_requests(__get_id(app))


@app.get("/users/<user_id>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user_connections(user_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: GET /users/user_id/follow
        Body: None
        Description: Retrieves all connections (followers, following) of a specific user
        Returns: Dictionary containing one list for followers and one for following. Each list contains of 0-many user objects.
    """
    connections = follower_service.get_user_connections(user_id)
    user_connections = UserConnections()

    for follower in connections['followers']:
        follower_item = user_service.get_user(follower)
        user_connections.followers.append(follower_item)

    for following in connections['following']:
        following_item = user_service.get_user(following)
        user_connections.following.append(following_item)

    return user_connections


def __get_id(app):
    user_id = app.context.get('claims').get('sub')
    if '|' in user_id:
        user_id = user_id.split("|")[1]
    return user_id


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
