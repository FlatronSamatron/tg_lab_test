from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Session, get_session
from app.models.user import RoleEnum, UserOrm
from app.services.auth import AuthService


def get_current_user_id(request: Request):
    token = request.cookies.get('acces_token', None)

    if token is None:
        raise HTTPException(401, "token does't valid")
    
    data = AuthService().decode_token(token)

    return data['id']



UserIdDep = Annotated[int, Depends(get_current_user_id)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_chief(user_id: UserIdDep, session: SessionDep):
    user = await session.get(UserOrm, user_id)

    if not user or user.role != RoleEnum.chief:
        raise HTTPException(status_code=403, detail="Only chief can create expedition")
    
    return user

ChiefDep = Annotated[UserOrm, Depends(get_current_chief)]