from pydantic import BaseModel

class User(BaseModel):
        userId: int
        username: str
        firstName: str
        lastName: str