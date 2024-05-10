import sys

sys.path.insert(0, "/var/task/.venv/lib/python3.12/site-packages")
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Path
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import BadRequestError

from findme.authorization import Authorizer
from enum import Enum

from src.LocationRiddlesService import LocationRiddlesService
from src.ImageBucketRepository import ImageBucketRepository
from src.LocationRiddlesRepository import LocationRiddlesRepository
from src.UserMicroserviceClient import UserMicroserviceClient

tracer = Tracer()
logger = Logger()

cors_config = CORSConfig(allow_origin=os.environ.get("FRONTEND_ORIGIN"))
app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)
app.enable_swagger(path="/location-riddles/swagger")

authorizer = Authorizer(
    auth0_domain=os.environ.get("AUTH0_DOMAIN"),
    auth0_audience=os.environ.get("AUTH0_AUDIENCE"),
)

image_bucket_repository = ImageBucketRepository()
location_riddle_repository = LocationRiddlesRepository()
user_microservice_client = UserMicroserviceClient()
location_riddles_service = LocationRiddlesService(
    location_riddle_repository, image_bucket_repository, user_microservice_client
)


class RequestBodyAttribute(Enum):
    FINDME_USERNAME = "https://api.find-me.life/username"
    LOCATION = "location"
    IMAGE = "image"
    GUESS = "guess"
    COMMENT = "comment"
    RATING = "rating"
    ARENAS = "arenas"


@app.post("/location-riddles")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_location_riddles():
    """
    Endpoint: POST /location-riddles
    Body: {
        "image": <image_file>,
        "location": <coordinate_list> e.g. [12.345, 67.890]
        "arenas": <arena_list> e.g. ["arena1", "arena2"]
    }
    Description: Creates a new location riddle with the provided image and location.
    Returns: A message indicating the successful upload of the location riddle.
    """
    return location_riddles_service.post_location_riddle(
        __get_attribute_from_request_body(RequestBodyAttribute.IMAGE.value, app),
        __get_attribute_from_request_body(RequestBodyAttribute.LOCATION.value, app),
        __get_attribute_from_request_body(RequestBodyAttribute.ARENAS.value, app),
        __get_username(),
    )


@app.post("/location-riddles/<location_riddle_id>/guess")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_guess_to_location_riddle(location_riddle_id: Annotated[str, Path()]):
    """
    Endpoint: POST /location-riddles/<location_riddle_id>/guess
    Body: {
        "guess": <coordinate_list> e.g. [12.345, 67.890]
    }
    Description: Submits a guess for a specific location riddle.
    Returns: The updated location riddle with the new guess
        and the distance to the correct location and the achieved score in the format:
        {
        "location_riddle": {<location_riddle>},
        "guess_result": {"distance": <distance>, "received_score": <score>}
        }
    """
    return location_riddles_service.guess_location_riddle(
        app.current_event,
        location_riddle_id,
        __get_username(),
        __get_attribute_from_request_body(RequestBodyAttribute.GUESS.value, app),
    )


@app.post("/location-riddles/<location_riddle_id>/comment")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_comment_to_location_riddle(location_riddle_id: Annotated[str, Path()]):
    """
    Endpoint: POST /location-riddles/<location_riddle_id>/comment
    Body: {
        "comment": <comment_string>
    }
    Description: Adds a comment to a specific location riddle.
    Returns: The updated location riddle with the new comment.
    """
    return location_riddles_service.comment_location_riddle(
        location_riddle_id,
        __get_username(),
        __get_attribute_from_request_body(RequestBodyAttribute.COMMENT.value, app),
    )


@app.get("/location-riddles")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles():
    """
    Endpoint: GET /location-riddles
    Body: None
    Description: Retrieves all location riddles of all users I follow.
    Returns: A list of location riddles.
    """
    return location_riddles_service.get_location_riddles_feed(
        app.current_event, __get_username()
    )


@app.get("/location-riddles/arena/<arena_name>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_arena(arena_name: Annotated[str, Path()]):
    """
    Endpoint: GET /location-riddles/arena/<arena>
    Body: None
    Description: Retrieves all location riddles that contain the requested arena.
    Returns: A list of location riddles.
    """
    return location_riddles_service.get_location_riddles_arena(
        arena_name, __get_username()
    )


@app.get("/location-riddles/user/<username>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_user(username: Annotated[str, Path()]):
    """
    Endpoint: GET /location-riddles/user/<username>
    Body: None
    Description: Retrieves all location riddles for a specific user.
    Returns: A list of location riddles.
    """
    return location_riddles_service.get_location_riddles_for_user(
        username=username, requester_username=__get_username()
    )


@app.get("/location-riddles/user")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_user():
    """
    Endpoint: GET /location-riddles/user
    Body: None
    Description: Retrieves all location riddles for the current user.
    Returns: A list of location riddles.
    """
    return location_riddles_service.get_location_riddles_for_user(
        username=__get_username(), requester_username=__get_username()
    )


@app.get("/location-riddles/user/<username>/solved")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_solved_location_riddles_by_user(username: Annotated[str, Path()]):
    """
    Endpoint: GET /location-riddles/user/<username>/solved
    Body: None
    Description: Retrieves all solved location riddles for a specific user.
    Returns: A list of location riddles.
    """
    return location_riddles_service.get_solved_location_riddles_for_user(
        app.current_event, username=username, requester_username=__get_username()
    )


@app.get("/location-riddles/user/solved")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_solved_location_riddles_by_user():
    """
    Endpoint: GET /location-riddles/user
    Body: None
    Description: Retrieves all solved location riddles for the current user.
    Returns: A list of location riddles.
    """
    return location_riddles_service.get_solved_location_riddles_for_user(
        app.current_event,
        username=__get_username(),
        requester_username=__get_username(),
    )


@app.get("/location-riddles/<location_riddle_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_location_riddle_id(
        location_riddle_id: Annotated[str, Path()],
):
    """
    Endpoint: GET /location-riddles/<location_riddle_id>
    Body: None
    Description: Retrieves a specific location riddle by its ID.
    Returns: The requested location riddle.
    """
    return location_riddles_service.get_location_riddle(
        location_riddle_id, __get_username()
    )


@app.post("/location-riddles/<location_riddle_id>/rate")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def rate_location_riddle(location_riddle_id: Annotated[str, Path()]):
    """
    Endpoint: POST /location-riddles/<location_riddle_id>/rate
    Body: {
        "rating": <rating_integer>
    }
    Description: Rates a specific location riddle.
    Returns: The updated location riddle with the new rating.
    """
    return location_riddles_service.rate_location_riddle(
        location_riddle_id,
        __get_username(),
        __get_attribute_from_request_body(RequestBodyAttribute.RATING.value, app),
    )


@app.delete("/location-riddles/<location_riddle_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def delete_location_riddles_by_location_riddle_id(
        location_riddle_id: Annotated[str, Path()],
):
    """
    Endpoint: DELETE /location-riddles/<location_riddle_id>
    Body: None
    Description: Deletes a specific location riddle by its ID.
    Returns: A message indicating the successful deletion of the location riddle.
    """
    return location_riddles_service.delete_location_riddle(
        location_riddle_id, __get_username()
    )


def __get_username():
    return app.context.get("claims").get(RequestBodyAttribute.FINDME_USERNAME.value)


def __get_attribute_from_request_body(attribute, app):
    try:
        return app.current_event.json_body[attribute]
    except KeyError:
        raise BadRequestError(f"Missing attribute {attribute} in request body")


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
