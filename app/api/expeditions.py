from fastapi import APIRouter, HTTPException
from sqlalchemy import func, insert, select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.api.dependencies import ChiefDep, SessionDep, UserIdDep
from app.models.expedition import ExpeditionOrm, StatusEnum
from app.models.expedition_member import ExpeditionMemberOrm, StateEnum
from app.models.user import RoleEnum, UserOrm
from app.schemas.expedition import ExpeditionCreate, ExpeditionResponse
from app.schemas.expedition_member import MemberInvite, MemberResponse

router = APIRouter(tags=["EXPEDITIONS"], prefix="/expeditions")

@router.post("/")
async def creaate_expedition(exp: ExpeditionCreate, chief: ChiefDep, session: SessionDep):
    new_expedition = ExpeditionOrm(**exp.model_dump(), chief_id=chief.id)

    session.add(new_expedition)
    await session.commit()
    await session.refresh(new_expedition)

    return new_expedition


@router.get("/", response_model=list[ExpeditionResponse])
async def get_expeditions(session: SessionDep):
    query = select(ExpeditionOrm)
    res = await session.execute(query)

    return res.scalars().all()

"""
Дозволені лише такі переходи:
- `draft -> ready`
- `ready -> active`
- `active -> finished`

draft:
- Статус встановлюється автоматично під час створення.
- На цьому етапі chief формує склад: запрошує учасників, учасники підтверджують участь.

ready:
- У цей статус переводить лише chief
- Перед переходом перевіряється, що експедиція ще не active/finished.

active:
- У цей статус переводить лише chief
- Перед стартом одночасно мають бути істинні всі умови:
start_at <= now().
Кількість confirmed учасників >= 2.
Кількість confirmed учасників <= capacity.
Жоден confirmed учасник не має перебувати в іншій active експедиції.

finished:
- Дозволено тільки з active.
- Після finished експедиція вважається завершеною: повторний start/set-ready заборонені.

"""
@router.patch("/{id}/status", response_model=ExpeditionResponse)
async def edit_expedition_status(new_status: StatusEnum, id: int, session: SessionDep, chief: ChiefDep):
    allowed_transitions = {
        StatusEnum.draft: [StatusEnum.ready],
        StatusEnum.ready: [StatusEnum.active],
        StatusEnum.active: [StatusEnum.finished],
        StatusEnum.finished: []                   
    }

    exp = await session.get(ExpeditionOrm, id)

    if not exp:
        raise HTTPException(status_code=404, detail="Expedition not found")
    
    if chief.id != exp.chief_id:
        raise HTTPException(status_code=403, detail="You can only edit your own expeditions")
    
    if new_status not in allowed_transitions[exp.status]:
        raise HTTPException(status_code=400, detail=f"Cannot change status from {exp.status} to {new_status}")

    if new_status == StatusEnum.active:
        if exp.start_at <= datetime.now():
            raise HTTPException(status_code=403, detail="date must be before start expedition")
        
        count_query = await session.execute(select(func.count(ExpeditionMemberOrm.id)).where(
            ExpeditionMemberOrm.expedition_id == exp.id,
            ExpeditionMemberOrm.state == StateEnum.confirmed
        ))

        confirmed_cnt = count_query.scalar_one()

        if confirmed_cnt < 2:
            raise HTTPException(400, "Confirmed members must be greater or equal 2")

        if confirmed_cnt < exp.capacity:
            raise HTTPException(400, "Not enough confirmed members to get ready")
        
        current_members_subquery = select(ExpeditionMemberOrm.user_id).where(
            ExpeditionMemberOrm.expedition_id == exp.id,
            ExpeditionMemberOrm.state == StateEnum.confirmed
        )
        
        conflict_query = select(ExpeditionMemberOrm).join(ExpeditionOrm).where(
            ExpeditionMemberOrm.user_id.in_(current_members_subquery),
            ExpeditionMemberOrm.state == StateEnum.confirmed,
            ExpeditionOrm.status == StatusEnum.active,
            ExpeditionOrm.id != exp.id
        )

        conflict = (await session.execute(conflict_query)).first()

        if conflict:
            raise HTTPException(status_code=400, detail="One of the members is already in another active expedition")
        
        
    exp.status = new_status

    await session.commit()
    await session.refresh(exp)

    return exp

"""
Правила запрошень
- Запрошувати можна лише користувачів з роллю member.
- Не можна запрошувати одного й того самого учасника в ту саму експедицію повторно.
- Підтверджувати може лише сам запрошений користувач.
- Підтвердити можна лише стан invited -> confirmed.
"""
@router.post("/{id}/members", response_model=MemberResponse)
async def add_member_to_exp(id: int, member: MemberInvite, session: SessionDep, chief: ChiefDep):
    exp = await session.get(ExpeditionOrm, id)

    if not exp:
        raise HTTPException(status_code=404, detail="Expedition not found")
    
    if chief.id != exp.chief_id:
        raise HTTPException(status_code=403, detail="You can only add members into your own expeditions")
    
    user_query = await session.execute(select(UserOrm).where(UserOrm.email == member.user_email))
    user = user_query.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == RoleEnum.chief:
        raise HTTPException(status_code=400, detail="You can only invite users with role 'member'")
    
    exp_member_query = await session.execute(select(ExpeditionMemberOrm).where(
        ExpeditionMemberOrm.user_id == user.id,
        ExpeditionMemberOrm.expedition_id == id
    ))

    exp_member = exp_member_query.scalar_one_or_none()

    if exp_member:
        raise HTTPException(status_code=400, detail="User already added")
    

    new_member_exp = ExpeditionMemberOrm(
        expedition_id = id,
        user_id = user.id,
    )

    session.add(new_member_exp)
    await session.commit()
    await session.refresh(new_member_exp)

    return new_member_exp


@router.patch("/{id}/members/confirm")
async def confirm_exp(id: int, user_id: UserIdDep, session: SessionDep):
    user = await session.get(UserOrm, user_id)

    if not user or user.role == RoleEnum.chief:
        raise HTTPException(status_code=400, detail="Status can confirm only member")
    
    user_exp_query = await session.execute(select(ExpeditionMemberOrm).where(
        ExpeditionMemberOrm.user_id == user.id,
        ExpeditionMemberOrm.expedition_id == id
    ))

    user_exp = user_exp_query.scalar_one_or_none()

    if user_exp is None:
        raise HTTPException(status_code=404, detail="You weren't invited")

    if user_exp.state == StateEnum.confirmed:
        raise HTTPException(status_code=404, detail="Your expedition was confirmed")
    
    user_exp.state = StateEnum.confirmed

    await session.commit()

    return {
        "status": "Your expedition was confirmed"
    }



    
    
    


    


