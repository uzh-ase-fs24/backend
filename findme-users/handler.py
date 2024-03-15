from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Path
from src.UserService import UserService
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver()

user_service = UserService()


@app.post("/users")
@tracer.capture_method
def post_user():
    return user_service.post_user(app.current_event.json_body)


@app.get("/users/<id>")
@tracer.capture_method
def get_user(id: Annotated[int, Path(lt=999)]):
    return user_service.get_user(int(id))


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
