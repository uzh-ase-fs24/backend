import sys

sys.path.insert(0, "/var/task/.venv/lib/python3.12/site-packages")
import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.event_handler.openapi.params import Path
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.utilities.typing import LambdaContext

from findme.authorization import Authorizer

from src.UserService import UserService

tracer = Tracer()
logger = Logger()

cors_config = CORSConfig(allow_origin=os.environ.get("FRONTEND_ORIGIN"))
app = APIGatewayRestResolver(cors=cors_config)

authorizer = Authorizer(
    auth0_domain=os.environ.get("AUTH0_DOMAIN"),
    auth0_audience=os.environ.get("AUTH0_AUDIENCE"),
)
user_service = UserService()


@app.post("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def post_user():
    # Get user id from oauth token
    userId = app.context.get('claims').get('sub')
    return user_service.post_user(app.current_event.json_body, userId)


@app.get("/users/<userId>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user(userId: Annotated[int, Path(lt=999)]):
    # Get user id from oauth token
    return user_service.get_user(userId)

@app.get("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_individual_user():
    # Get user id from oauth token
    userId = app.context.get('claims').get('sub')
    return user_service.get_user(userId)


@app.put("/users")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user():
    # Get user id from oauth token
    id = app.context.get('claims').get('sub')
    return user_service.update_user(app.current_event.json_body, id)


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
