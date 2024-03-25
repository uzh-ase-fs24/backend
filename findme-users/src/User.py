from pydantic import BaseModel

class User(BaseModel):
        userId: str
        username: str
        firstName: str
        lastName: str