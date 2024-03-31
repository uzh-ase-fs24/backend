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

from src.UserService import UserService
from src.FollowerService import FollowerService

tracer = Tracer()
logger = Logger()

cors_config = CORSConfig(allow_origin=os.environ.get("FRONTEND_ORIGIN"))
app = APIGatewayRestResolver(cors=cors_config)

authorizer = Authorizer(
    auth0_domain=os.environ.get("AUTH0_DOMAIN"),
    auth0_audience=os.environ.get("AUTH0_AUDIENCE"),
)
user_service = UserService()

follower_service = FollowerService()


@app.post("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_user():
    user_id = app.context.get('claims').get('sub')
    if '|' in user_id:
        user_id = user_id.split("|")[1]
    return user_service.post_user(app.current_event.json_body, user_id)


@app.get("/users/<user_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user(user_id: Annotated[int, Path(lt=999)]):
    return user_service.get_user(user_id)


@app.get("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_individual_user():
    user_id = app.context.get('claims').get('sub')
    if '|' in user_id:
        user_id = user_id.split("|")[1]
    return user_service.get_user(user_id)


@app.get("/users/search")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_similar_users():
    username = app.current_event.query_string_parameters.get("username")
    return user_service.get_similar_users(username)


@app.put("/users/<user_id>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def follow_user(user_id: Annotated[int, Path(lt=999)]):
    requestee_id = app.context.get('claims').get('sub')
    return follower_service.create_follower_request(requestee_id, user_id)


@app.patch("/users/<requester_id>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def update_follow_user(requester_id: Annotated[int, Path(lt=999)]):
    requestee_id = app.context.get('claims').get('sub')
    action = app.current_event.query_string_parameters.get("action")
    if action == "accept":
        return follower_service.accept_follow_request(requester_id, requestee_id)
    if action == "declined":
        return follower_service.create_follower_request(requester_id, requestee_id)
    else:
        raise BadRequestError(f"Action {action} does not exist, please provide a valid value (accept/decline)")


@app.get("/users/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_received_follow_requests():
    user_id = app.context.get('claims').get('sub')
    return follower_service.get_received_follow_requests(user_id)


@app.get("/users/<user_id>/follow")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user_connections(user_id: Annotated[int, Path(lt=999)]):
    return follower_service.get_user_connections(user_id)


@app.put("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user():
    user_id = app.context.get('claims').get('sub')
    if '|' in user_id:
        user_id = user_id.split("|")[1]
    return user_service.update_user(app.current_event.json_body, user_id)


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
