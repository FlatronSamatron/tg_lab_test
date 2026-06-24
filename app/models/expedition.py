import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.expedition_member import ExpeditionMemberOrm
from app.models.user import UserOrm

class StatusEnum(str, enum.Enum):
    draft = "draft"
    ready = "ready"
    active = "active"
    finished = "finished"


class ExpeditionOrm(Base, TimestampMixin):

    __tablename__ = "expeditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[StatusEnum] = mapped_column(default=StatusEnum.draft)
    start_at: Mapped[datetime.datetime]
    end_at: Mapped[datetime.datetime] = mapped_column(nullable=True)
    capacity: Mapped[int]
    chief_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    chief: Mapped["UserOrm"] = relationship(back_populates="expeditions")
    members: Mapped[list["ExpeditionMemberOrm"]] = relationship(back_populates="expedition")
