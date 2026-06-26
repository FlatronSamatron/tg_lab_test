from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from app.services.websocket import manager
from app.services.auth import AuthService
from app.api.dependencies import SessionDep
from app.models.expedition import ExpeditionOrm
from app.models.expedition_member import ExpeditionMemberOrm


router = APIRouter(tags=["WEBSOCKETS"])

@router.websocket("/ws/expeditions/{id}")
async def websocket_expedition(websocket: WebSocket, id: int, session: SessionDep):
    token = websocket.cookies.get('acces_token')
    if not token:
        await websocket.close(code=1008)
        return
        
    try:
        data = AuthService().decode_token(token)
        user_id = data['id']
    except Exception:
        await websocket.close(code=1008)
        return

    exp = await session.get(ExpeditionOrm, id)
    
    if not exp:
        await websocket.close(code=1008)
        return
        
    if exp.chief_id != user_id:
        member_query = select(ExpeditionMemberOrm).where(
            ExpeditionMemberOrm.expedition_id == id,
            ExpeditionMemberOrm.user_id == user_id
        )

        member = (await session.execute(member_query)).scalar_one_or_none()
        
        if not member:
            await websocket.close(code=1008)
            return
        
    await manager.connect(websocket, id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, id)