from enum import Enum


class PartitionKey(Enum):
    USER = "USER"
    REQUEST = "REQUEST"
    FOLLOWERS = "FOLLOWERS"
    FOLLOWING = "FOLLOWING"

