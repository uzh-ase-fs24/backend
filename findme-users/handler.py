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
    return user_service.post_user(app.current_event.json_body)


@app.get("/users/<id>")
@tracer.capture_method
@authorizer.requires_auth(app=app)
def get_user(id: Annotated[int, Path(lt=999)]):
    return user_service.get_user(int(id))


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
