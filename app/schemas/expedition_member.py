import datetime

from pydantic import BaseModel, EmailStr

from app.models.expedition_member import StateEnum

class MemberInvite(BaseModel):
    user_email: EmailStr

class MemberResponse(BaseModel):
    id: int
    expedition_id: int
    user_id: int
    state: StateEnum
    invited_at: datetime.datetime