from abc import ABC, abstractmethod


class AbstractImageBucketRepository(ABC):

    @abstractmethod
    def post_image_to_s3(self, image_base64: str, key: str):
        pass

    @abstractmethod
    def get_image_from_s3(self, key: str):
        pass

    @abstractmethod
    def delete_image_from_s3(self, key: str):
        pass
