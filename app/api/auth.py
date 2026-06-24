from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.dependencies import SessionDep, UserIdDep
from app.db import get_session
from app.models.user import UserOrm
from app.schemas.user import UserCreate, UserGet, UserResponse
from app.services.auth import AuthService

auth_service = AuthService()

router = APIRouter(tags=["AUTH"], prefix="/auth")

@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, session: SessionDep):
    password = auth_service.get_password_hash(data.password)
    user = data.model_dump(exclude={"password"})
    new_user = UserOrm(**user, hashed_password=password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

@router.post("/login")
async def login(data: UserGet, response: Response, session: SessionDep):
    query = select(UserOrm).filter_by(email=data.email)
    res = await session.execute(query)

    user = res.scalars().one_or_none()

    if not user or not auth_service.verify_password(data.password, user.hashed_password): # type: ignore
        raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    acces_token = auth_service.create_access_token({"id": user.id}) # type: ignore
    response.set_cookie("acces_token", acces_token)

    return {"acces_token": acces_token}


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie("acces_token")

    return {"status": "success"}
    

@router.get('/me', response_model=UserResponse)
async def get_me(user_id: UserIdDep, session: SessionDep):
    return await session.get(UserOrm, user_id)
