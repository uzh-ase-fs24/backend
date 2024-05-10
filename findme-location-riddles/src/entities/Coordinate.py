from decimal import Decimal
from typing import List

from pydantic import BaseModel, field_validator, ValidationError


class Coordinate(BaseModel):
    coordinate: List[Decimal]

    @field_validator('coordinate')
    def validate_coordinate(cls, v):
        if len(v) != 2:
            raise ValidationError('location should contain 2 values: latitude and longitude')
        return v
