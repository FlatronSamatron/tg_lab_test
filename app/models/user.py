import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base, TimestampMixin
from app.models.expedition import ExpeditionOrm
from app.models.expedition_member import ExpeditionMemberOrm

class RoleEnum(str, enum.Enum):
    chief = "chief"
    member = "member"

class UserOrm(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    role: Mapped[RoleEnum] = mapped_column(default=RoleEnum.member)

    expeditions: Mapped[list["ExpeditionOrm"]] = relationship(back_populates="chief")
    participations: Mapped[list["ExpeditionMemberOrm"]] = relationship(back_populates="user")