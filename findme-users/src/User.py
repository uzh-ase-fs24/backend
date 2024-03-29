from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    username: str
    first_name: str
    last_name: str
