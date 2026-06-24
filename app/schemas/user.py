from pydantic import BaseModel, ConfigDict, Field, EmailStr
import datetime

from app.models.user import RoleEnum

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=3, max_length=10)
    role: RoleEnum = RoleEnum.member

class UserGet(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: RoleEnum
    created_at: datetime.datetime


