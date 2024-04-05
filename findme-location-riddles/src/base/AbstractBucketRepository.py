from abc import ABC, abstractmethod


class AbstractBucketRepository(ABC):

    @abstractmethod
    def post_image_to_s3(self, image_base64, key):
        pass

    @abstractmethod
    def get_image_from_s3(self, key):
        pass

    @abstractmethod
    def delete_image_from_s3(self, key):
        pass