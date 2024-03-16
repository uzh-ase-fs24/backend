from pydantic import BaseModel

class UserDto(BaseModel):
        userId: int
        username: str
        firstName: str
        lastName: str