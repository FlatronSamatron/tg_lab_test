import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.expedition import StatusEnum
from app.schemas.user import UserResponse

class ExpeditionCreate(BaseModel):
    title: str
    description: str
    capacity: int = Field(gt=0)
    start_at: datetime.datetime

    @field_validator("start_at")
    @classmethod
    def remove_timezone(cls, v: datetime.datetime):
        if v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class ExpeditionResponse(BaseModel):
    id: int
    title: str
    description: str
    capacity: int = Field(gt=0)
    status: StatusEnum
    chief: UserResponse
    created_at: datetime.datetime


class ExpeditionStatusUpdate(BaseModel):
    new_status: StatusEnum