from sqlalchemy.exc import IntegrityError

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse


from app.api.auth import router as auth_router
from app.api.expeditions import router as epedition_router
from app.api.ws import router as ws_router

app = FastAPI()


# @app.exception_handler(IntegrityError)
# async def error_handler(request: Request, exc: IntegrityError):
#     return JSONResponse(
#         status_code=400,
#         content={"detail": "Something went wrong"}
#     )


@app.get("/health")
async def get_health():
    return {
        "status": "OK"
    }

@app.get("/ws_test")
async def open_ws_tester():
    with open("test/ws.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


app.include_router(auth_router)
app.include_router(epedition_router)
app.include_router(ws_router)