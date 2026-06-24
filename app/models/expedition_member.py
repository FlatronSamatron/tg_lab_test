import datetime
import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from app.db import Base
from app.models.expedition import ExpeditionOrm
from app.models.user import UserOrm

class StateEnum(str, enum.Enum):
    invited = "invited"
    confirmed = "confirmed"


class ExpeditionMemberOrm(Base):
    __tablename__ = "expedition_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    expedition_id: Mapped[int] = mapped_column(ForeignKey("expeditions.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    state: Mapped[StateEnum] = mapped_column(default=StateEnum.invited)
    invited_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    confirmed_at: Mapped[datetime.datetime] = mapped_column(nullable=True)

    expedition: Mapped["ExpeditionOrm"] = relationship(back_populates="members")
    user: Mapped["UserOrm"] = relationship(back_populates="participations")