import boto3
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


@app.get("/")
@tracer.capture_method
def hello_world():
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')  # Replace 'your-region' with your AWS region
    #
    # # Get reference to the users table
    table = dynamodb.Table('usersTable')
    
    response = table.get_item(Key={'username': 'j.alba'})

    if 'Item' in response:
        item = response['Item']
        print("User found:")
        print("User ID:", item['userId'])
        print("First Name:", item['firstName'])
        print("Last Name:", item['lastName'])
        print("Username:", item['username'])
    else:
        print("User not found.")
    return {"message": "Hello World"}


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
