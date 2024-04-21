from pydantic import BaseModel, field_validator, ValidationError
from typing import List
from decimal import Decimal


class Guess(BaseModel):
    user_id: str
    guess: List[Decimal]

    @field_validator('guess')
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValidationError('Coordinate should contain 2 values: latitude and longitude')
        # ToDo: implement validation for latitude and longitude for coordinates used in frontend
        # if not (-90 <= v[0] <= 90):
        #     raise ValidationError('Latitude should be between -90 and 90')
        # if not (-180 <= v[1] <= 180):
        #     raise ValidationError('Longitude should be between -180 and 180')
        return v
