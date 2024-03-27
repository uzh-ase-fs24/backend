import boto3
import base64
from botocore.exceptions import ClientError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class ImageBucketRepository:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket_name = 'ase-findme-image-upload-bucket'

    def post_image_to_s3(self, image_base64, key):
        image_data = base64.b64decode(image_base64)

        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType='image/png'
            )
            return {"message": "Image uploaded successfully"}
        except ClientError as e:
            raise BadRequestError(f"Error saving image to bucket: {e}")

    def get_image_from_s3(self, user_id):
        image_data = self.__get_image_data_from_s3(user_id)

        if image_data:
            encoded_image = base64.b64encode(image_data).decode('utf-8')

            return {
                "image_base64": encoded_image,
                "Content-Type": "image/png"
            }
        else:
            raise BadRequestError("Failed to retrieve image from S3")

    def __get_image_data_from_s3(self, user_id):
        key = f"{user_id}-image1.png"

        try:
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            image_data = response['Body'].read()
            return image_data
        except ClientError as e:
            raise BadRequestError(f"Error retrieving image from S3: {e}")
