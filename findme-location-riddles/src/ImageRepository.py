import boto3
import base64
from botocore.exceptions import ClientError
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)


class ImageRepository:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def post_image_to_s3(self, image_base64):
        image_data = base64.b64decode(image_base64)

        try:
            # Upload the image to S3
            self.s3.put_object(
                Bucket='imageuploadbucket',
                Key='uploaded_image.png',
                Body=image_data,
                ContentType='image/png'
            )
            return {"message": "Image uploaded successfully"}
        except ClientError as e:
            raise BadRequestError(f"Error saving image to bucket: {e}")

