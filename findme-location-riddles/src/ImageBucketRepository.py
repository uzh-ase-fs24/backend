import base64
import boto3
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
)
from botocore.exceptions import ClientError
from botocore.client import Config


from .base.AbstractImageBucketRepository import AbstractImageBucketRepository


class ImageBucketRepository(AbstractImageBucketRepository):
    def __init__(self):
        region = "eu-central-2"
        s3_config = Config(
            region_name=region,
            signature_version="s3v4",
        )

        self.s3 = boto3.client("s3", region_name=region, config=s3_config)
        self.bucket_name = "ase-findme-image-upload-bucket"

    def post_image_to_s3(self, image_base64: str, key: str) -> dict:
        image_data = base64.b64decode(image_base64)

        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType="image/png",
            )
            return {"message": "Image uploaded successfully"}
        except ClientError as e:
            raise BadRequestError(f"Error saving image to bucket: {e}")

    def get_image_from_s3(self, key: str) -> str:
        return self.create_pre_signed_image_url(key)

    def create_pre_signed_image_url(
        self, key: str, client_method: str = "get_object"
    ) -> str:
        try:
            url = self.s3.generate_presigned_url(
                client_method,
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=3600,
            )
            return url
        except ClientError as e:
            raise BadRequestError(f"Error generating presigned URL: {e}")

    def delete_image_from_s3(self, key: str) -> dict:
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            return {"message": "Image deleted successfully"}
        except ClientError as e:
            raise BadRequestError(f"Error deleting image from bucket: {e}")

    def __get_image_data_from_s3(self, key: str):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            image_data = response["Body"].read()
            return image_data
        except ClientError as e:
            raise BadRequestError(f"Error retrieving image from S3: {e}")
