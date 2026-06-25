from fastapi import APIRouter, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from app.api.dependencies import ChiefDep, SessionDep
from app.models.expedition import ExpeditionOrm, StatusEnum
from app.schemas.expedition import ExpeditionCreate, ExpeditionResponse

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


@router.patch("/{id}/status", response_model=ExpeditionResponse)
async def edit_expedition_status(new_status: StatusEnum,id: int, session: SessionDep, chief: ChiefDep):
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
        from datetime import datetime, timezone
        exp.start_at = datetime.now()

    exp.status = new_status

    await session.commit()
    await session.refresh(exp)

    return exp
    


