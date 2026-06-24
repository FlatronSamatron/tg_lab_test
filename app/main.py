from sqlalchemy.exc import IntegrityError

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.models import expedition, expedition_member


from app.api.auth import router as auth_router

app = FastAPI()


@app.exception_handler(IntegrityError)
async def error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Something went wrong"}
    )


@app.get("/health")
async def get_health():
    return {
        "status": "OK"
    }


app.include_router(auth_router)