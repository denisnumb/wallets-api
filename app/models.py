from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class WalletsOrm(Base):
    __tablename__ = 'wallets'
    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    balance: Mapped[float] = mapped_column(default=0)