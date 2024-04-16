import sys

sys.path.insert(0, "/var/task/.venv/lib/python3.12/site-packages")
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Path
from aws_lambda_powertools.utilities.typing import LambdaContext

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
    return location_riddles_service.post_location_riddle(app.current_event.json_body['image'], __get_id(app))


@app.get("/location-riddles")  # get all location riddles of users I follow
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_user():
    return location_riddles_service.get_location_riddles_feed(app.current_event, __get_id(app))


@app.get("/location-riddles/user/<user_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_user(user_id: Annotated[int, Path(lt=999)]):
    return location_riddles_service.get_location_riddles_for_user(user_id)


@app.get("/location-riddles/user")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_user():
    return location_riddles_service.get_location_riddles_for_user(__get_id(app))


@app.get("/location-riddles/<location_riddle_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_location_riddles_by_location_riddle_id(location_riddle_id: Annotated[int, Path(lt=999)]):
    return location_riddles_service.get_location_riddle(location_riddle_id)


@app.patch("/location-riddles/<location_riddle_id>/rate")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def rate_location_riddle(location_riddle_id: Annotated[int, Path(lt=999)]):
    user_id = __get_id(app)
    return location_riddles_service.rate_location_riddle(location_riddle_id, user_id,
                                                         app.current_event.json_body['rating'])


@app.delete("/location-riddles/<location_riddle_id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def delete_location_riddles_by_location_riddle_id(location_riddle_id: Annotated[int, Path(lt=999)]):
    return location_riddles_service.delete_location_riddle(location_riddle_id, __get_id(app))


def __get_id(app):
    user_id = app.context.get('claims').get('sub')
    if '|' in user_id:
        user_id = user_id.split("|")[1]
    return user_id


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
