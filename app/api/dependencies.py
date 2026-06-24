from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Session, get_session
from app.services.auth import AuthService


def get_current_user_id(request: Request):
    token = request.cookies.get('acces_token', None)

    if token is None:
        raise HTTPException(401, "token does't valid")
    
    data = AuthService().decode_token(token)

    return data['id']



UserIdDep = Annotated[int, Depends(get_current_user_id)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]