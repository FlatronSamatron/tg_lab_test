from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL)

class Base(DeclarativeBase):
    pass


Session = async_sessionmaker(engine, expire_on_commit=False)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


async def get_session():
    async with Session() as session:
        yield session