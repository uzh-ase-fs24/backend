import sys

sys.path.insert(0, "/var/task/.venv/lib/python3.12/site-packages")
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Path
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError
)

from findme.authorization import Authorizer

from src.LocationRiddlesService import LocationRiddlesService
from src.ImageBucketRepository import ImageBucketRepository
from src.LocationRiddlesRepository import LocationRiddlesRepository

tracer = Tracer()
logger = Logger()

cors_config = CORSConfig(allow_origin=os.environ.get("FRONTEND_ORIGIN"))
app = APIGatewayRestResolver(cors=cors_config)

authorizer = Authorizer(
    auth0_domain=os.environ.get("AUTH0_DOMAIN"),
    auth0_audience=os.environ.get("AUTH0_AUDIENCE"),
)

image_bucket_repository = ImageBucketRepository()
location_riddle_repository = LocationRiddlesRepository()
location_riddles_service = LocationRiddlesService(location_riddle_repository, image_bucket_repository)


@app.post("/location-riddles")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_location_riddles():
    """
        Endpoint: POST /location-riddles
        Body: {
            "image": <image_file>,
            "location": <coordinate_list> e.g. [12.345, 67.890]
        }
        Description: Creates a new location riddle with the provided image and location.
        Returns: A message indicating the successful upload of the location riddle.
    """
    return location_riddles_service.post_location_riddle(__get_attribute("image", app),
                                                         __get_attribute("location", app),
                                                         __get_id(app))


@app.post("/location-riddles/<location_riddle_id>/guess")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_guess_to_location_riddle(location_riddle_id: Annotated[int, Path(lt=999)]):
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
    return location_riddles_service.guess_location_riddle(app.current_event,
                                                          location_riddle_id,
                                                          __get_id(app),
                                                          __get_attribute("guess", app))


@app.post("/location-riddles/<location_riddle_id>/comment")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_comment_to_location_riddle(location_riddle_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: POST /location-riddles/<location_riddle_id>/comment
        Body: {
            "comment": <comment_string>
        }
        Description: Adds a comment to a specific location riddle.
        Returns: The updated location riddle with the new comment.
    """
    return location_riddles_service.comment_location_riddle(location_riddle_id, __get_id(app),
                                                            __get_attribute("comment", app))


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
    return location_riddles_service.get_location_riddles_feed(app.current_event, __get_id(app))


@app.get("/location-riddles/user/<user_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_user(user_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: GET /location-riddles/user/<user_id>
        Body: None
        Description: Retrieves all location riddles for a specific user.
        Returns: A list of location riddles.
    """
    return location_riddles_service.get_location_riddles_for_user(user_id)


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
    return location_riddles_service.get_location_riddles_for_user(__get_id(app))


@app.get("/location-riddles/<location_riddle_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_location_riddle_id(location_riddle_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: GET /location-riddles/<location_riddle_id>
        Body: None
        Description: Retrieves a specific location riddle by its ID.
        Returns: The requested location riddle.
    """
    return location_riddles_service.get_location_riddle(location_riddle_id)


@app.post("/location-riddles/<location_riddle_id>/rate")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def rate_location_riddle(location_riddle_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: POST /location-riddles/<location_riddle_id>/rate
        Body: {
            "rating": <rating_integer>
        }
        Description: Rates a specific location riddle.
        Returns: The updated location riddle with the new rating.
    """
    return location_riddles_service.rate_location_riddle(location_riddle_id, __get_id(app),
                                                         __get_attribute("rating", app))


@app.delete("/location-riddles/<location_riddle_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def delete_location_riddles_by_location_riddle_id(location_riddle_id: Annotated[int, Path(lt=999)]):
    """
        Endpoint: DELETE /location-riddles/<location_riddle_id>
        Body: None
        Description: Deletes a specific location riddle by its ID.
        Returns: A message indicating the successful deletion of the location riddle.
    """
    return location_riddles_service.delete_location_riddle(location_riddle_id, __get_id(app))


def __get_id(app):
    user_id = app.context.get('claims').get('sub')
    if '|' in user_id:
        user_id = user_id.split("|")[1]
    return user_id


def __get_attribute(attribute, app):
    try:
        return app.current_event.json_body[attribute]
    except KeyError:
        raise BadRequestError(f"Missing attribute {attribute} in request body")


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
