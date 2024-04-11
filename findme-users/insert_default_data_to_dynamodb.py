
import boto3
from botocore.exceptions import ClientError


def insert_default_data_to_dynamodb():
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-2')
    table = dynamodb.Table('usersTable')

    try:
        items = table.scan()['Items']

        if not items:
            users = [
                {"user_id": '660e5fc5de3e93a3b75f51a8', "username": 'user1', "first_name": 'John', "last_name": 'Doe'},
                {"user_id": '660e5fc5de3e93a3b75f51a9', "username": 'user2', "first_name": 'Jane', "last_name": 'Doe'},
                {"user_id": '660e5fc5de3e93a3b75f51aa', "username": 'user3', "first_name": 'Jim', "last_name": 'Doe'},
                {"user_id": '660e5fc5de3e93a3b75f51ab', "username": 'user4', "first_name": 'Jill', "last_name": 'Doe'},
                {"user_id": '660e5fc5de3e93a3b75f51ac', "username": 'user5', "first_name": 'Jack', "last_name": 'Doe'}
            ]

        for user in users:
            user['partition_key'] = "USER"
            table.put_item(Item=user)

    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")


if __name__ == "__main__":
    insert_default_data_to_dynamodb()