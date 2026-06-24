import enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base, TimestampMixin

class RoleEnum(str, enum.Enum):
    chief = "chief"
    member = "member"

class UserOrm(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    role: Mapped[RoleEnum] = mapped_column(default=RoleEnum.member)